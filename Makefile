CLUSTER_USERDATA_FILES = \
	 userdata.d/ciquery.yaml \
	 userdata.d/kube-wrangler.yaml \
	 userdata.d/docker_service.yaml \
	 userdata.d/flannel_config.yaml \
	 userdata.d/flanneld_service.yaml \
	 userdata.d/modules_load.yaml \
	 configure-cluster

DISCOVERY_USERDATA_FILES = \
	userdata.d/ciquery.yaml \
	configure-discovery

GENERATED = \
	userdata-cluster \
	userdata-discovery \
	userdata.d/ciquery.yaml \
	userdata.d/kube-wrangler.yaml

all: userdata-cluster userdata-discovery

userdata-discovery: $(DISCOVERY_USERDATA_FILES)
	write-mime-multipart.py -M 'dict(recurse_array)+list(append)+str()' $^ > $@ || rm -f $@

userdata-cluster: $(CLUSTER_USERDATA_FILES)
	write-mime-multipart.py -M 'dict(recurse_array)+list(append)+str()' $^ > $@ || rm -f $@

userdata.d/ciquery.yaml: userdata.d/ciquery.yaml.in ciquery.py
	cat userdata.d/ciquery.yaml.in > $@
	sed "s/^/      /" ciquery.py >> $@

userdata.d/kube-wrangler.yaml: userdata.d/kube-wrangler.yaml.in kube-wrangler.py
	cat userdata.d/kube-wrangler.yaml.in > $@
	sed "s/^/      /" kube-wrangler.py >> $@

clean:
	rm -f $(GENERATED)
