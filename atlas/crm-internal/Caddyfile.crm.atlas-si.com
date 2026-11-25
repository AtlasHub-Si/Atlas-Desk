# Reverse proxy Caddy para crm.atlas-si.com (CRM Interno do Grupo AtlasHub.SI)
crm.atlas-si.com {
	encode gzip
	route {
		# Bloqueia webhook global do WAHA na internet pública (WAHA fala apenas na rede Docker interna)
		@waha_global path /api/v1/webhooks/waha
		respond @waha_global 403

		reverse_proxy 127.0.0.1:3000
	}
}
