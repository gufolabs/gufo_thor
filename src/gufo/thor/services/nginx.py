# ---------------------------------------------------------------------
# Gufo Thor: nginx service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
nginx service.

Attributes:
    nginx: nginx service singleton.
"""

# Python modules
import os
import subprocess
from typing import Any, Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..log import logger
from .base import BaseService
from .login import login
from .traefik import traefik


class NginxService(BaseService):
    name = "nginx"
    dependencies = (traefik, login)
    SUBJ_PATH = "etc/nginx/ssl/domain_name.txt"
    RSA_KEY_SIZE = 4096
    CERT_SUBJ = "/C=IT/ST=Milano/L=Milano/O=Gufo Labs/OU=Gufo Thor"
    CERT_DAYS = 3650

    def get_compose_image(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "nginx:stable"

    def get_compose_volumes(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        r = ["./etc/nginx:/etc/nginx"]
        if config.noc.path:
            # Use /ui from repo
            r += [f"{config.noc.path}/ui:/opt/noc/ui"]
        else:
            # Use /ui from container
            ...
        return r

    def get_compose_networks(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        return {
            "ipv4_address": "172.20.0.100",
            "aliases": ["nginx", config.expose.domain_name],
        }

    def get_compose_ports(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return [f"{config.expose.port}:443"]

    def get_compose_dirs(
        self: "NginxService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[List[str]]:
        return ["etc/nginx/conf.d", "etc/nginx/ssl"]

    def prepare_compose_config(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        # Prepare nginx.conf
        path = "etc/nginx/nginx.conf"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(NGINX_CONF)
        # Prepare mime.types
        path = "etc/nginx/mime.types"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(MIME_TYPES)
        # Prepare noc.conf
        path = "etc/nginx/conf.d/noc.conf"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(
                NOC_CONF.replace(
                    "{domain_name}", config.expose.domain_name
                ).replace("{port}", str(config.expose.port))
            )
        # Prepare TLS certificates
        if self._to_rebuild_certificate(config):
            self._rebuild_certificate(config)

    def _to_rebuild_certificate(self: "NginxService", config: Config) -> bool:
        """Check if SSL certificate must be rebuilt."""
        if not os.path.exists(self.SUBJ_PATH):
            return True
        with open(self.SUBJ_PATH) as fp:
            return fp.read() != self.get_cert_subj(config)

    def get_cert_subj(self: "NginxService", config: Config) -> str:
        """Get certificate subj."""
        return f"{self.CERT_SUBJ}/CN={config.expose.domain_name}"

    def _rebuild_certificate(self: "NginxService", config: Config) -> None:
        """Rebuild SSL certificates."""
        # Generate key
        key_path = "etc/nginx/ssl/noc.key"
        logger.info("Generating private key: %s", key_path)
        subprocess.check_call(
            ["openssl", "genrsa", "-out", key_path, str(self.RSA_KEY_SIZE)]
        )
        # Create CSR
        csr_path = "etc/nginx/ssl/noc.csr"
        logger.info("Generating certificate signing request: %s", csr_path)
        subprocess.check_call(
            [
                "openssl",
                "req",
                "-key",
                key_path,
                "-new",
                "-out",
                csr_path,
                "-subj",
                self.get_cert_subj(config),
            ]
        )
        # Generate certificate
        cert_path = "etc/nginx/ssl/noc.crt"
        logger.info("Generating certificate: %s", cert_path)
        subprocess.check_call(
            [
                "openssl",
                "x509",
                "-signkey",
                key_path,
                "-in",
                csr_path,
                "-req",
                "-days",
                str(self.CERT_DAYS),
                "-out",
                cert_path,
            ]
        )
        # Write subj
        logger.info("Writing %s", self.SUBJ_PATH)
        with open(self.SUBJ_PATH, "w") as fp:
            fp.write(self.get_cert_subj(config))


NGINX_CONF = """user nginx;
worker_processes 1;

events {
    worker_connections  1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 10;
    include /etc/nginx/conf.d/*.conf;
    access_log /dev/stdout;
    error_log /dev/stdout;
}
"""

MIME_TYPES = """types {
    text/html                             html htm shtml;
    text/css                              css;
    text/xml                              xml;
    image/gif                             gif;
    image/jpeg                            jpeg jpg;
    application/javascript                js;
    application/atom+xml                  atom;
    application/rss+xml                   rss;

    text/mathml                           mml;
    text/plain                            txt;
    text/vnd.sun.j2me.app-descriptor      jad;
    text/vnd.wap.wml                      wml;
    text/x-component                      htc;

    image/png                             png;
    image/tiff                            tif tiff;
    image/vnd.wap.wbmp                    wbmp;
    image/x-icon                          ico;
    image/x-jng                           jng;
    image/x-ms-bmp                        bmp;
    image/svg+xml                         svg svgz;
    image/webp                            webp;

    application/font-woff                 woff;
    application/java-archive              jar war ear;
    application/json                      json;
    application/mac-binhex40              hqx;
    application/msword                    doc;
    application/pdf                       pdf;
    application/postscript                ps eps ai;
    application/rtf                       rtf;
    application/vnd.apple.mpegurl         m3u8;
    application/vnd.ms-excel              xls;
    application/vnd.ms-fontobject         eot;
    application/vnd.ms-powerpoint         ppt;
    application/vnd.wap.wmlc              wmlc;
    application/vnd.google-earth.kml+xml  kml;
    application/vnd.google-earth.kmz      kmz;
    application/x-7z-compressed           7z;
    application/x-cocoa                   cco;
    application/x-java-archive-diff       jardiff;
    application/x-java-jnlp-file          jnlp;
    application/x-makeself                run;
    application/x-perl                    pl pm;
    application/x-pilot                   prc pdb;
    application/x-rar-compressed          rar;
    application/x-redhat-package-manager  rpm;
    application/x-sea                     sea;
    application/x-shockwave-flash         swf;
    application/x-stuffit                 sit;
    application/x-tcl                     tcl tk;
    application/x-x509-ca-cert            der pem crt;
    application/x-xpinstall               xpi;
    application/xhtml+xml                 xhtml;
    application/xspf+xml                  xspf;
    application/zip                       zip;

    application/octet-stream              bin exe dll;
    application/octet-stream              deb;
    application/octet-stream              dmg;
    application/octet-stream              iso img;
    application/octet-stream              msi msp msm;

    application/vnd.openxmlformats-officedocument.wordprocessingml.document    docx;
    application/vnd.openxmlformats-officedocument.spreadsheetml.sheet          xlsx;
    application/vnd.openxmlformats-officedocument.presentationml.presentation  pptx;

    audio/midi                            mid midi kar;
    audio/mpeg                            mp3;
    audio/ogg                             ogg;
    audio/x-m4a                           m4a;
    audio/x-realaudio                     ra;

    video/3gpp                            3gpp 3gp;
    video/mp2t                            ts;
    video/mp4                             mp4;
    video/mpeg                            mpeg mpg;
    video/quicktime                       mov;
    video/webm                            webm;
    video/x-flv                           flv;
    video/x-m4v                           m4v;
    video/x-mng                           mng;
    video/x-ms-asf                        asx asf;
    video/x-ms-wmv                        wmv;
    video/x-msvideo                       avi;
}
"""

NOC_CONF = """upstream traefik {
    server noc-traefik-1:80;
}

log_format timed_combined '$remote_addr - $remote_user [$time_local] '
    '"$request" $status $body_bytes_sent '
    '"$http_referer" "$http_user_agent" '
    '$request_time $upstream_response_time $pipe';

server {
    listen 443 ssl http2;
    server_name {domain_name};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_certificate /etc/nginx/ssl/noc.crt;
    ssl_certificate_key /etc/nginx/ssl/noc.key;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains";
    add_header X-Content-Type-Options nosniff;
    ssl_stapling off;
    ssl_stapling_verify off;

    location @error401 {
        return 302 $scheme://$host:{port}/ui/login/index.html?uri=$request_uri;
    }

    # Login service api
    location /api/auth/ {
        internal;
        proxy_pass http://traefik;
        #rewrite  ^/api/auth/(.*)  /api/login/$1 break;
        # internal;
        gzip on;
        gzip_types text/css text/x-js;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Original-URI $request_uri;
        proxy_set_header Content-Length '0';
    }

    # Login service api
    location /api/login/ {
        proxy_pass http://traefik;
        gzip on;
        gzip_types text/css text/x-js;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Original-URI $request_uri;
    }

    # Card service api
    location /api/ {
        proxy_pass http://traefik;
        auth_request /api/auth/auth/;
        gzip on;
        gzip_types text/css text/x-js;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        auth_request_set $user $upstream_http_remote_user;
        proxy_set_header Remote-User $user;
        auth_request_set $groups $upstream_http_remote_groups;
        proxy_set_header Remote-Groups $groups;
        auth_request_set $apiaccess $upstream_http_x_noc_api_access;
        proxy_set_header X-NOC-API-Access $apiaccess;
    }

    # UI files
    location ^~ /ui/ {
        alias /opt/noc/ui/;
        gzip on;
        gzip_types text/css text/x-js application/javascript;
    }

    location / {
        rewrite ^/$ /main/desktop/;
        proxy_pass http://traefik;
        auth_request /api/auth/auth/;
        proxy_read_timeout 900;
        gzip on;
        gzip_types text/css text/x-js;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        auth_request_set $user $upstream_http_remote_user;
        proxy_set_header Remote-User $user;
        auth_request_set $groups $upstream_http_remote_groups;
        proxy_set_header Remote-Groups $groups;
        # Proxy authentication settings
        error_page 401 = @error401;
    }
}
"""

nginx = NginxService()
