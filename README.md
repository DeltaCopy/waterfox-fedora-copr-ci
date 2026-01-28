# waterfox-fedora-copr-ci

[Waterfox](https://github.com/BrowserWorks/waterfox) is an open-source, privacy-focused browser based on the popular open source browser with a red panda as a mascot. It is designed to be a drop-in replacement for said browser that offers enhanced privacy features, performance improvements, and customizability while maintaining compatibility with existing extensions.

Building from src is a resource intensive process, and as a result this package uses the release tarball from https://cdn.waterfox.com/waterfox/releases/

A GitHub actions workflow is scheduled to run daily at 12AM to check the latest version released from https://github.com/BrowserWorks/waterfox

The COPR project repository is available from: https://copr.fedorainfracloud.org/coprs/deltacopy/waterfox

## Active releases available

- Fedora 42
- Fedora 43
- Fedora rawhide

# Instructions

Enable the COPR repository then install the package.

<pre>
sudo dnf copr enable deltacopy/waterfox
sudo dnf in waterfox
</pre>

# Default search engine

Changed from Startpage to use DuckDuckGo

<h3> COPR build status </h3> 

[![Copr build status](https://copr.fedorainfracloud.org/coprs/deltacopy/waterfox/package/waterfox/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/deltacopy/waterfox/package/waterfox/)

<h3> GitHub action workflow status </h3> 

[![Waterfox Fedora COPR CI](https://github.com/DeltaCopy/waterfox-fedora-copr-ci/actions/workflows/waterfox-ci.yml/badge.svg)](https://github.com/DeltaCopy/waterfox-fedora-copr-ci/actions/workflows/waterfox-ci.yml)
