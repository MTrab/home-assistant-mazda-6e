# Introduction

This component has been created to be used with Home Assistant.

Mazda 6e presents a possibility to connect your Mazda 6e vehicle to Home Assistant.
This integration accepts your email and password and encrypts them internally. A device ID is generated automatically and retained for reauthentication. Enter the verification code sent by email when requested. Existing entries remain compatible; no migration or manual device ID is needed. Plaintext credentials and passwords are not saved in the config entry.

# Installation

## With HACS

1. Add this repository as a custom repository in HACS.
2. Download the integration.
3. Restart Home Assistant

## Manual

Copy the `mazda_6e` directory, from `custom_components` in this repository,
and place it inside your Home Assistant Core installation's `custom_components` directory. Restart Home Assistant prior to moving on to the `Setup` section.

`Note`: If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository
