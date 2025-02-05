# kdevops-results-archive

<img src="images/kdevops-archive.png" width=250 align=center alt="kdevops archive logo">

This is a collection of results for tests run with
[kdevops](https://github.com/linux-kdevops/kdevops)
on different kernels. Each user has their own dedicated
namespace.

This git tree leverages git lfs, what this allow is for you to download
only a smaller version of the repository without the actual tarballs
of the results, you then can decide when and if you need the tarballs
by selectively downloading them with "git lfs fetch --include". As it
stands without LFS if you clone this git tree you'd have to download
218M, if you use GIT_LFS_SKIP_SMUDGE=1 before the clone to avoid downloading
all the files you'd just get a 2.5M directory, for a 98.85% of space savings.

To leverage LFS:

```bash
    GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/linux-kdevops/kdevops-results-archive.git
```

To get the file you want:

```
    git lfs fetch --include "fstests/mcgrof/xfs/libvirt-qemu/20240514-0001/6.9.0-rc6+.xz"
```

kdevops will automatically make use of the archive if you have it present.
To be clear, you should have both the kdevops and kdevops-results-archive
directory in the same parent directory. Do not put kdevops-results-archive
inside the kdevops directory.

# Submitting results

Please ensure you use `*.xz` tarballs, so, if you're going to push
results, we have a sanity check to ensure you don't push directories
with more than 5 files. To ensure this you can use:

```bash
git config core.hooksPath hooks
```

# Seeing tarball contents

To see contents you can use something like:

```
tar -tOJf fstests/mcgrof/xfs/libvirt-qemu/20240505-0001/6.9.0-rc6.xz 2>&1 | grep xfs | grep 033
```

# Seeing fstests results

To see fstests results you can use something like this:

```
tar -xOJf fstests/mcgrof/xfs/libvirt-qemu/20240505-0001/6.9.0-rc6.xz 6.9.0-rc6/xfs_reflink_1024/xfs/033.out.bad
tar -xOJf fstests/mcgrof/xfs/libvirt-qemu/20240505-0001/6.9.0-rc6.xz 6.9.0-rc6/xfs_reflink_1024/xfs/033.dmesg
```
