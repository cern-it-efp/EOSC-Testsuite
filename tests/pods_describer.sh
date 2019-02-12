sleep=5

while true; do
	echo ""
	kubectl describe pod train-mpijob-launcher #| grep kubelet,;
	sleep $sleep;
	clear;
	echo ""
	kubectl describe pod train-mpijob-worker-0 #| grep kubelet,;
        sleep $sleep;
	clear;
	echo ""
	kubectl describe pod train-mpijob-worker-1 #| grep kubelet,;
        sleep $sleep;
	clear;
	echo "";
	kubectl describe pod train-mpijob-worker-2
	sleep $sleep;
	clear;
done
