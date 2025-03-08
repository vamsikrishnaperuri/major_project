<?php
namespace local_studentperformance;

defined('MOODLE_INTERNAL') || die();

class performance_manager {
    /**
     * Get performance data for a specific course
     *
     * @param int $courseid
     * @return array
     */
    public static function get_course_performance_data($courseid) {
        global $DB;
        
        // Use cache to store performance data
        $cache = \cache::make('local_studentperformance', 'performance_data');
        $performance_data = $cache->get('data');
        
        if ($performance_data === false) {
            $json_file = __DIR__ . '/../data/performance_data.json';
            
            if (!file_exists($json_file)) {
                return [];
            }

            $performance_data = json_decode(file_get_contents($json_file), true);
            $cache->set('data', $performance_data);
        }
        
        // Filter data for the specific course
        $course_data = array_filter($performance_data, function($item) use ($courseid) {
            return $item['course_id'] == $courseid;
        });

        // Get user details for the performance data
        $user_data = [];
        foreach ($course_data as $data) {
            $user = $DB->get_record('user', ['id' => $data['user_id']], 'id, firstname, lastname');
            if ($user) {
                $user_data[] = [
                    'user_id' => $data['user_id'],
                    'fullname' => fullname($user),
                    'performance' => $data['Performance'],
                    'performance_class' => strtolower(str_replace(' ', '-', $data['Performance'])),
                    'last_updated' => userdate(time(), get_string('strftimerecent', 'core_langconfig'))
                ];
            }
        }

        return $user_data;
    }
}