FROM fedora:22
MAINTAINER Vitezslav Crhonek <vcrhonek@redhat.com>
RUN dnf install -y usbutils python-hwdata && rm -rf /var/cache/yum
