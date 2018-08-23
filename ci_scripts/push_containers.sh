export IMAGE_TAG=$(cat VERSION)
export AARCH=`uname -m`
cd containers/xos
docker build -f Dockerfile.base -t cachengo/xos-base:master .
cd ../..
docker build -f containers/xos/Dockerfile.libraries -t cachengo/xos-libraries:master .
docker build -f containers/xos/Dockerfile.xos-core -t cachengo/xos-core:master .
git clone https://github.com/opencord/chameleon.git -b master ./tmp.chameleon
docker build -f containers/chameleon/Dockerfile.chameleon -t cachengo/chameleon:master .
rm -r tmp.chameleon
git clone https://github.com/opencord/chameleon.git -b master ./containers/xos/tmp.chameleon
docker build -f containers/xos/Dockerfile.client -t cachengo/xos-client:master .
docker build -f containers/xos/Dockerfile.synchronizer-base -t cachengo/xos-synchronizer-base:master .

docker tag cachengo/xos-base:master cachengo/xos-base-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-core:master cachengo/xos-core-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-libraries:master cachengo/xos-libraries-$AARCH:$IMAGE_TAG
docker tag cachengo/chameleon:master cachengo/chameleon-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-client:master cachengo/xos-client-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-synchronizer-base:master cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG

docker push cachengo/xos-base-$AARCH:$IMAGE_TAG
docker push cachengo/xos-core-$AARCH:$IMAGE_TAG
docker push cachengo/xos-libraries-$AARCH:$IMAGE_TAG
docker push cachengo/chameleon-$AARCH:$IMAGE_TAG
docker push cachengo/xos-client-$AARCH:$IMAGE_TAG
docker push cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG
