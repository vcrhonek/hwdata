FROM fedora:37
MAINTAINER Vitezslav Crhonek <vcrhonek@redhat.com>
RUN dnf -y update && dnf -y install usbutils && dnf -y install python3-hwdata --setopt='tsflags=' && dnf clean all
