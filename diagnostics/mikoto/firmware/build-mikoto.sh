#!/bin/sh
set -eu
fixture_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture_container="qbf-mikoto-rebuild-$$"
fixture_image='zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5'
cleanup() { docker rm -f "$fixture_container" >/dev/null 2>&1 || true; }
trap cleanup EXIT HUP INT TERM
docker run -d --name "$fixture_container" "$fixture_image" sleep infinity >/dev/null
docker cp "$fixture_root/firmware/mikoto" "$fixture_container:/fixture-module"
docker cp "$fixture_root/dist/west-frozen.yml" "$fixture_container:/tmp/west-frozen.yml"
docker exec -i "$fixture_container" bash -s <<'BUILD'
set -euo pipefail
mkdir -p /work /out
cd /work
git init zmk
git -C zmk remote add origin https://github.com/zmkfirmware/zmk
git -C zmk fetch --depth 1 origin 4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85
git -C zmk checkout --detach FETCH_HEAD
cd zmk
west init -l app
cp /tmp/west-frozen.yml app/west-frozen.yml
west config manifest.file west-frozen.yml
west update --narrow -o=--depth=1
for revision in 5.20.0 6.1.0 6.3.0 7.2.0; do
    extra=()
    if [ "$revision" = 6.3.0 ]; then
        extra=(-DEXTRA_DTC_OVERLAY_FILE=/fixture-module/compat/mikoto-6.3.overlay)
    fi
    west build -s app -d "build-$revision" -b "mikoto@$revision//zmk" -- \
        -DSHIELD=mikoto_test -DZMK_EXTRA_MODULES=/fixture-module \
        -DZMK_CONFIG=/fixture-module/config "${extra[@]}"
    cp "build-$revision/zephyr/zmk.uf2" "/out/mikoto-test-$revision.uf2"
done
BUILD
docker cp "$fixture_container:/out/." "$fixture_root/dist/"
printf 'Built all four Mikoto test images in %s/dist\n' "$fixture_root"
