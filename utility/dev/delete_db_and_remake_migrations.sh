#!/bin/bash

. "`dirname \"$0\"`/functions.sh"

cd $MY_PATH
cd ../..

set -e # die on err

if [[ "no" == $(ask_yes_or_no "Delete migration code and wipe DB?") ]]
then
    echo "Skipped."
    exit 0
fi

echo "--- Deleting ALL migration code..."
rm -r openlab/accounts/migrations
rm -r openlab/discussion/migrations
rm -r openlab/gallery/migrations
rm -r openlab/moderation/migrations
rm -r openlab/newsletter/migrations
rm -r openlab/notifications/migrations
rm -r openlab/project/migrations
rm -r openlab/release/migrations
rm -r openlab/team/migrations
rm -r openlab/users/migrations
rm -r openlab/wiki/migrations

echo "--- Backing up default.sqlite3.db..."
mv default.sqlite3.db default.sqlite3.db.backup

echo "--- Rebuilding migrations..."
python manage.py makemigrations accounts discussion gallery moderation newsletter notifications project release team users wiki

echo "--- Syncing DB..."
python manage.py migrate

