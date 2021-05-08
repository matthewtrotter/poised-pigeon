
setup_containers:
	@docker-compose up -d poised_pigeon_test
	@sleep 2s
	@docker-compose up -d test_orchestrator


generate_test_certs:
	@git clone https://github.com/michaelklishin/tls-gen tls-gen
	@make -C tls-gen/basic PASSWORD=asdf1234
	@make -C tls-gen/basic verify
	@make -C tls-gen/basic info
	@mkdir -p ../rabbitmq/etc/ssl
	@mv -f tls-gen/basic/ca_certificate.pem ../rabbitmq/etc/ssl/ca_certificate.pem
	@mv -f tls-gen/basic/server_certificate.pem ../rabbitmq/etc/ssl/server_certificate.pem
	@mv -f tls-gen/basic/server_key.pem ../rabbitmq/etc/ssl/server_key.pem
	@rm -rf tls-gen
	