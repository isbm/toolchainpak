# toolchainpak

A little framework for packaging embedded toolchains.
The idea is to simply reuse already built packages in the repository,
and rewrap already built binaries as `noarch` under different naming.
This would allow to install in a containers specific toolchain for the
targets, those are provisioned from the same repositories.
