# Discord IDs dictionary: avoid using these directly in code

CID_SLIMEPING_CHANNEL = 887894832708730881
CID_BOTTESTING_CHANNEL = 887967982356148254
CID_DAILYSLIMERESULT_CHANNEL = 950051638075334686

GID_ULTRA_ROLE = 887894985398157363
GID_ALTRA_ROLE = 887915507804692511
GID_OUTRA_ROLE = 888058783891353630
GID_UNDER20_ROLE = 959225786844446820

GID_BOTCREATOR_ROLE = 930544543391186965
GID_TESTINGMYBOT_ROLE = 930546213294587935
GID_SLIMEPINGTEST_ROLE = 937694420952842270

UID_MAPLE = 253994447782543361
UID_GUNTHER = 315112026093649920
UID_TRAFFY = 120428736637173760
UID_VARIANT = 579199616143327258


# Grouped/wrapped IDs: you should use these in code, and you may change them temporarily in tests

MAIN_CHANNEL = CID_SLIMEPING_CHANNEL
REPORT_CHANNEL = CID_DAILYSLIMERESULT_CHANNEL
BOT_CHANNELS = {CID_SLIMEPING_CHANNEL, CID_BOTTESTING_CHANNEL}

BOT_ADMINS = {UID_MAPLE, UID_TRAFFY, UID_VARIANT}
DATA_ADMINS = {UID_MAPLE, UID_GUNTHER, UID_TRAFFY, UID_VARIANT}
PING_ROLES = {GID_ULTRA_ROLE, GID_ALTRA_ROLE}

MENTION_ULTRA_ROLE = f'<@&{GID_ULTRA_ROLE}>'
MENTION_ALTRA_ROLE = f'<@&{GID_ALTRA_ROLE}>'
MENTION_OUTRA_ROLE = f'<@&{GID_OUTRA_ROLE}>'
MENTION_UNDER20_ROLE = f'<@&{GID_UNDER20_ROLE}>'

MENTION_BOTCREATOR_ROLE = f'<@&{GID_BOTCREATOR_ROLE}>'
MENTION_TESTINGMYBOT_ROLE = f'<@&{GID_TESTINGMYBOT_ROLE}>'
MENTION_SLIMEPINGTEST_ROLE = f'<@&{GID_SLIMEPINGTEST_ROLE}>'

PING_MENTIONS = (MENTION_ULTRA_ROLE, MENTION_ALTRA_ROLE, MENTION_SLIMEPINGTEST_ROLE)

