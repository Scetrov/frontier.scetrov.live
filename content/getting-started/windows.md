+++
date = '2025-04-28T16:22:00+01:00'
title = 'Windows Tips'
weight = 50
+++

## Working with `pnpm` and `foundry` on Windows

> [!IMPORTANT]
> This is what worked for me, your mileage may vary. In general using Mac or Linux is a better Node and Foundry development experience than Windows.

Foundry has problems with Windows and the Lattice team don't support it in PowerShell, Windows PowerShell or cmd, there are known bugs with Foundry and Git Bash. This mean WSL is the best supported way of developing with Foundry on Windows.

If you are unable to use WSL then I suggest enabling Virtualization in the BIOS and using VirtualBox to create a Linux VM to develop within. Alternatively you can sign up to a cloud service like AWS, Azure or OVH and rent a virtual machine in the cloud for less than $5/month.

## Install WSL

You will need to be running Windows 10 (Build 19041) or Windows 11, you can use it on earlier versions of Windows 10 but you must go through the [manual install](https://learn.microsoft.com/en-us/windows/wsl/install-manual) process.

First from a PowerShell or Windows Command Prompt that is running as an administrator (Right Click -> Run as Administrator):

```shell
wsl --install
```

Second, ensure that WSL 2 is the default:
```shell
wsl --set-default-version 2
```
Third, install a Distribution of Linux:
```shell
wsl --install -d Ubuntu-24.04
```

> [!IMPORTANT]
> I recommend using Ubuntu 24.04 because it is the easiest distribution to search for solutions using Google or ChatGPT/Claude/etc. Other distributions are available, I tend to use Debian, Ubuntu, Arch and Nix.

Finally, I strongly recommend using [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/get-started) to access WSL as this supports all of the features of modern terminal emulators and thus means you are less likely to run into issues with formatting and compatibility.

## Install Docker Desktop

Make sure to [install](https://docs.docker.com/desktop/install/windows-install/) and start Docker Desktop, and if prompted select the "WSL 2 backend".

Once Docker Desktop is installed click the "Settings Cog" in the top right hand corner of the Docker Desktop window.

From there navigate to **Resources** → **WSL Integration** and check the slider next to the WSL Distribution you are using, i.e. "Ubuntu" or "Ubuntu-24.04".

## Setting up Tools

From here on the [CCP Documentation](https://docs.evefrontier.com/QuickstartGuide) works flawlessly.

## Troubleshoot WSL Install Issues

If you want to start over with WSL because something has gone very wrong, then you can unregister and reregister the distribution to reset it:

```
wsl -l -v
```

This will result in something like this:

```
  NAME                      STATE           VERSION
* docker-desktop-data       Stopped         2
  Ubuntu-24.04              Stopped         2
  docker-desktop            Stopped         2
```

You only want to unregister the **Ubuntu-24.04** distribution with the following command:

```
wsl --unregister Ubuntu-24.04
```

You can then re-register the distribution by following [Setting Up Your Tools](https://docs.evefrontier.com/Tools) starting from:

```
wsl --install -d Ubuntu-24.04
```

## Frequent Disconnection from WSL

If you are using WSL as a shell or with VSCode, and you find yourself frequently being disconnected from the container, try disabling the Resource Saver in Docker Desktop.

1. In settings (the gear in the upper right),
2. Select Resources then the Advanced section,
3. Uncheck the **Enable Resource Saver**,
4. Restart Docker Desktop.
