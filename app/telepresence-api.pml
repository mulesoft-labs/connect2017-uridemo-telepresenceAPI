<?xml version="1.0" encoding="UTF-8" ?>
<Package name="telepresence-api" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="." xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="icon" src="icon.png" />
        <File name="main" src="scripts/main.py" />
        <File name="cert" src="scripts/server.pem" />
        <File name="__init__" src="scripts/stk/__init__.py" />
        <File name="events" src="scripts/stk/events.py" />
        <File name="logging" src="scripts/stk/logging.py" />
        <File name="runner" src="scripts/stk/runner.py" />
        <File name="services" src="scripts/stk/services.py" />
    </Resources>
    <Topics />
    <IgnoredPaths>
        <Path src=".DS_Store" />
        <Path src=".metadata" />
        <Path src="scripts/main_no_NAO.py" />
        <Path src="scripts/main_orig.py" />
        <Path src="scripts/server.pem" />
    </IgnoredPaths>
</Package>
