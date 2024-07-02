# ssh url of your server
SSHDIR=
# ftp url of your server
FTPDIR=
# ssh and ftp password
PASS=
# directory on your server to install files
SRVDIR=
# public url of your directory
# (leave it empty if the root of your website)
URLDIR=

#include secret.mk

help:
	@echo index.cgi, mount, umount, save, sftp, ssh, install

data/societaires.sqlite:
	sqlite3 data/societaires.sqlite < schema.sql

index.cgi: index.py
	@echo creating $@
	@sed -e "s/path_root = '.*'/path_root = ''/g" \
		-e "s;url = '';url = '$(URLDIR)/index.cgi';g" \
		-e "s/debug(True)/debug(False)/" \
		-e "s/run(.*/run(server='cgi')/" \
		$< > $@
	@chmod 755 $@

pass:
	@echo -n $(PASS) | wl-copy

mount: pass
	mkdir $@
	sshfs $(SSHDIR):$(SRVDIR) $@ -C -p 22

umount:
	fusermount3 -u mount
	rmdir mount

backup: pass
	@mkdir mount
	@sshfs $(SSHDIR):$(SRVDIR) mount -C -p 22
	@echo "Creating backup/$$(date +%Y%m%d)-societaires.sqlite"
	@cp mount/data/societaires.sqlite backup/$$(date +%Y%m%d)-societaires.sqlite
	@fusermount3 -u mount
	@rmdir mount

sftp: pass
	sftp $(FTPDIR)

ssh: pass
	export TERM=xterm-256color; ssh $(SSHDIR) -p 22

scp: pass
	@echo scp file $(SSHDIR):$(SRVDIR)/

install: index.cgi pass
	@mkdir mount
	@sshfs $(SSHDIR):$(SRVDIR) mount -C -p 22
	@cp index.cgi mount/
	@cp bottle.py mount/
	@cp htaccess mount/.htaccess
	@cp -r views mount/
	@cp -r assets mount/
	@cp -r scripts mount/
	@fusermount3 -u mount
	@rmdir mount

clean:
	rm -f index.cgi

.PHONY: pass backup install sftp ssh scp
