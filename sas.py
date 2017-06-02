from safir_notification_service.alarm.alarm_handler import AlarmHandler
from safir_notification_service.report.report_generator import ReportGenerator
from safir_notification_service.utils.repeated_timer import RepeatedTimer


class SafirAlarmService:
    def __init__(self):
        self.alarm_thread_list = []
        self.report_thread_list = []

    @staticmethod
    def process_alarm(alarm_id, current_state, previous_state, reason,
                      openstack_config, panel_config):
        alarm_handler = AlarmHandler(openstack_config, panel_config)
        alarm_handler.handle_alarm(alarm_id,
                                   current_state,
                                   previous_state,
                                   reason)

    def send_report(self, email_addr, report_interval,
                    openstack_config, panel_config):
        report_generator = ReportGenerator(email_addr,
                                           openstack_config,
                                           panel_config)
        rt = RepeatedTimer(report_interval, report_generator.generate_report)
        self.report_thread_list.append(rt)

    def kill_report_threads(self):
        for rt in self.report_thread_list:
            print ('killing report thread')
            rt.stop()
