# One2Track GPS watch
Integration to get One2Track watches/trackers information from the [web portal](https://www.one2trackgps.com/auth/users/sign_in)

## Current features:
 - Single device with a device tracker and multiple sensors
 - Attributes in device tracker is used as source
 - Detects HA zones
 - Detects multiple devices in your account

## Feature roadmap (PRs welcome)
 - Add services:
   - Send message (through Home Assistant notify)
   - Force update button
   - Set Signal strength sensor to show graph instead of numeric
   - Set Satellite count sensor to show graph instead of numeric
   - Set Altitude sensor to show graph instead of numeric

# Installation
The best method is using HACS (https://hacs.xyz)
1.  Make sure you have hacs installed
2.  Add this repository as custom repository to hacs by going to hacs, integrations, click on the three dots in the upper right corner and click on custom repositories
3.  In the repository field, fill in the link to this repository (https://github.com/renedis/one2track) and for category, select Integration. Click on Add
4.  Go back to hacs, integrations and add click on the blue button Explore and download repositories in the bottom left corner, search for One2Track and install it
5.  Reboot HA
6.  In HA goto Config -> Integrations. Add the One2Track to HA
7.  Enter your username and password

# Example
![Example](https://community-assets.home-assistant.io/original/4X/8/1/3/813fb34f4f0613381a3467cd35833b3b00de2657.png)
