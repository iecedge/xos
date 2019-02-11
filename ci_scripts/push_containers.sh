export IMAGE_TAG=$(cat VERSION)
export AARCH=`uname -m`
cd containers/xos
docker build -f Dockerfile.base -t cachengo/xos-base:$IMAGE_TAG .
cd ../..
docker build -f containers/xos/Dockerfile.libraries -t cachengo/xos-libraries:$IMAGE_TAG .
docker build -f containers/xos/Dockerfile.xos-core -t cachengo/xos-core:$IMAGE_TAG .
git clone https://github.com/opencord/chameleon.git -b master ./tmp.chameleon
docker build -f containers/chameleon/Dockerfile.chameleon -t cachengo/chameleon:$IMAGE_TAG .
rm -r tmp.chameleon
git clone https://github.com/opencord/chameleon.git -b master ./containers/xos/tmp.chameleon
docker build -f containers/xos/Dockerfile.client -t cachengo/xos-client:$IMAGE_TAG .
docker build -f containers/xos/Dockerfile.synchronizer-base -t cachengo/xos-synchronizer-base:$IMAGE_TAG .

docker tag cachengo/xos-base:$IMAGE_TAG cachengo/xos-base-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-core:$IMAGE_TAG cachengo/xos-core-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-libraries:$IMAGE_TAG cachengo/xos-libraries-$AARCH:$IMAGE_TAG
docker tag cachengo/chameleon:$IMAGE_TAG cachengo/chameleon-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-client:$IMAGE_TAG cachengo/xos-client-$AARCH:$IMAGE_TAG
docker tag cachengo/xos-synchronizer-base:$IMAGE_TAG cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG

docker push cachengo/xos-base-$AARCH:$IMAGE_TAG
docker push cachengo/xos-core-$AARCH:$IMAGE_TAG
docker push cachengo/xos-libraries-$AARCH:$IMAGE_TAG
docker push cachengo/chameleon-$AARCH:$IMAGE_TAG
docker push cachengo/xos-client-$AARCH:$IMAGE_TAG
docker push cachengo/xos-synchronizer-base-$AARCH:$IMAGE_TAG
