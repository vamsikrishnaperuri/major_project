<?php
namespace local_studentperformance;

defined('MOODLE_INTERNAL') || die();

class performance_updater {
    private $python_script_path;
    private $data_file_path;

    public function __construct() {
        $this->python_script_path = __DIR__ . '/../python/get_performance.py';
        $this->data_file_path = __DIR__ . '/../data/performance_data.json';
    }

    /**
     * Update performance data
     * @return bool
     */
    public function update_performance_data() {
        global $CFG;

        // Ensure data directory exists
        $data_dir = dirname($this->data_file_path);
        if (!is_dir($data_dir)) {
            mkdir($data_dir, 0755, true);
        }

        // Execute Python script
        $command = escapeshellcmd($CFG->python_path . ' ' . $this->python_script_path);
        $output = shell_exec($command);
        
        if ($output === null) {
            debugging('Failed to execute Python script', DEBUG_DEVELOPER);
            return false;
        }

        // Validate JSON output
        $data = json_decode($output, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            debugging('Invalid JSON output from Python script', DEBUG_DEVELOPER);
            return false;
        }

        // Save new data
        $success = file_put_contents($this->data_file_path, $output);
        
        // Clear cache
        \cache_helper::purge_by_event('local_studentperformance_data_updated');

        return $success !== false;
    }
}
