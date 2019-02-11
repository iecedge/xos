export IMAGE_TAG=$(cat VERSION)
export AARCH=`uname -m`
cd containers/xos
docker build -f Dockerfile.base -t cachengo/xos-base-$AARCH:$IMAGE_TAG .
cd ../..
docker build -f containers/xos/Dockerfile.libraries -t cachengo/xos-libraries-$AARCH:$IMAGE_TAG .
docker build -f containers/xos/Dockerfile.xos-core -t cachengo/xos-core-$AARCH:$IMAGE_TAG .
git clone https://github.com/opencord/chameleon.git -b master ./tmp.chameleon
docker build -f containers/chameleon/Dockerfile.chameleon -t cachengo/chameleon-$AARCH:$IMAGE_TAG .
rm -r tmp.chameleon
git clone https://github.com/opencord/chameleon.git -b master ./containers/xos/tmp.chameleon
docker build -f containers/xos/Dockerfile.client -t cachengo/xos-client-$AARCH:$IMAGE_TAG .
docker build -f containers/xos/Dockerfile.synchronizer-base -t cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG .

docker push cachengo/xos-base-$AARCH:$IMAGE_TAG
docker push cachengo/xos-core-$AARCH:$IMAGE_TAG
docker push cachengo/xos-libraries-$AARCH:$IMAGE_TAG
docker push cachengo/chameleon-$AARCH:$IMAGE_TAG
docker push cachengo/xos-client-$AARCH:$IMAGE_TAG
docker push cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG
