<?php
defined('MOODLE_INTERNAL') || die();

function xmldb_gradereport_userperformance_upgrade($oldversion) {
    global $DB;

    $dbman = $DB->get_manager();

    // Example: Adding a new column (if needed)
    if ($oldversion < 2025030401) {
        $table = new xmldb_table('gradereport_userperformance_data');
        $field = new xmldb_field('lastupdated', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, '0', 'performance');

        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }

        upgrade_plugin_savepoint(true, 2025030401, 'gradereport', 'userperformance');
    }

    return true;
}
