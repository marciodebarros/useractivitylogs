import datetime
from datetime import timedelta


class FileSummary:
    'Represents the summary of a file loaded'

    def __init__(self):
        """Initalized a new instance of the FileSummary object and initializes the counters"""
        self.file_name=''
        self.file_start_date_time = ''
        self.file_end_date_time = ''
        self.elapsed_time = ''
        self.logins=0
        self.launches=0
        self.enterings=0
        self.exits=0
        self.accesses=0
        self.logouts=0
        self.timeouts=0
        self.rejects=0

    def toJSON(self):
        return dict(
            file_name = self.file_name,
            start_date_time=datetime.datetime.fromtimestamp(self.file_start_date_time).isoformat(),
            end_date_time=datetime.datetime.fromtimestamp(self.file_end_date_time).isoformat(),
            elapsed_processing_time=str(self.get_elapsed_process_time()),
            logins_count = self.logins,
            launches_count = self.launches,
            enterings_count = self.enterings,
            exiting_count = self.exits,
            accessing_count = self.accesses,
            logouts_count = self.logouts,
            timeouts_count = self.timeouts,
            rejects_count = self.rejects
        )


    def set_file_name(self, file_name):
        "Set the file name"
        self.file_name = file_name

    def count_logged_in(self):
        "Increments the counter for the log in action"
        self.logins += 1

    def count_lauched(self):
        "Increments the counter for the launched in action"
        self.launches += 1

    def count_entered(self):
        "Increments the counter for the entered in action"
        self.enterings += 1

    def count_exited(self):
        "Increments the counter for the exited in action"
        self.exits += 1

    def count_accessed(self):
        "Increments the counter for the accessed in action"
        self.accesses += 1

    def count_logged_out(self):
        "Increments the counter for the log out action"
        self.logouts += 1

    def count_timed_out(self):
        "Increments the counter for the time out action"
        self.timeouts += 1

    def count_rejects(self):
        "Increment the counter for the rejected records"
        self.rejects += 1

    def get_file_name(self):
        "Return the name of the file being processed"
        return self.file_name

    def get_logged_in(self):
        "Return the total of log in actions"
        return self.logins

    def get_launched(self):
        "Return the total of launch actions"
        return self.launches

    def get_entered(self):
        "Return the total of entered actions"
        return self.enterings

    def get_exited(self):
        "Return the total of exited actions"
        return self.exits

    def get_accessed(self):
        "Return the total of accessed actions"
        return self.accesses

    def get_logged_out(self):
        "Return the total of log out actions"
        return self.logouts

    def get_time_out(self):
        "Return the total of time out actions"
        return self.timeouts

    def get_rejects(self):
        "Retrurn the total of reject records"
        return self.rejects

    def get_file_start_date_time(self):
        "Returns the date/time when the batch started to be processed."
        return datetime.datetime.fromtimestamp(self.file_start_date_time).isoformat()

    def set_file_start_date_time(self):
        "Set the date/time when the batch started to be processed."
        self.file_start_date_time = datetime.datetime.now().timestamp()

    def get_file_end_date_time(self):
        "Returns the date/time when the batch finished processing"
        return datetime.datetime.fromtimestamp(self.file_end_date_time).isoformat()

    def set_file_end_date_time(self):
        "Set the date/time when the batch finished to be processed."
        self.file_end_date_time = datetime.datetime.now().timestamp()

    def get_elapsed_process_time(self):
        "Returns the time elapsed to process the batch"
        elapsed_time = ''
        if not (self.file_start_date_time is None) and not (self.file_end_date_time is None):
            elapsed_time = self.file_end_date_time - self.file_start_date_time
        return str(timedelta(seconds=elapsed_time))



class BatchSummary:
    'Represents the summary of all files loaded in a batch'

    def __init__(self):
        '''Initalized a new instance of the BatchSummary object and initializes the counters'''
        self.total_of_files = 0
        self.total_logins = 0
        self.total_launches = 0
        self.total_enterings = 0
        self.total_exits = 0
        self.total_accesses = 0
        self.total_logouts = 0
        self.total_timeouts = 0
        self.total_rejects = 0
        self.files_in_batch = []
        self.batch_start_date_time = ''
        self.batch_end_date_time = ''

    def toJSON(self):
        return dict(total_of_files=self.total_of_files,
                    batch_start_date_time = datetime.datetime.fromtimestamp(self.batch_start_date_time).isoformat(),
                    batch_end_date_time = datetime.datetime.fromtimestamp(self.batch_end_date_time).isoformat(),
                    elapsed_processing_time = str(self.get_elapsed_process_time()),
                    total_logins = self.total_logins,total_launches = self.total_launches,
                    total_enterings = self.total_enterings, total_exits = self.total_exits,
                    total_accesses = self.total_accesses, total_logouts = self.total_logouts,
                    total_timeouts = self.total_timeouts, total_rejects = self.total_rejects,
                    files = [file.toJSON() for file in self.files_in_batch])

    def add_file(self, file_stats: FileSummary):
        "Add one more tile to the summary count"
        self.total_of_files += 1
        self.add_log_ins(file_stats.get_logged_in())
        self.add_launches(file_stats.get_launched())
        self.add_entering(file_stats.get_entered())
        self.add_exits(file_stats.get_exited())
        self.add_accesses(file_stats.get_accessed())
        self.add_log_outs(file_stats.get_logged_out())
        self.add_timeouts(file_stats.get_time_out())
        self.add_rejects(file_stats.get_rejects())
        self.files_in_batch.append(file_stats)

    def add_log_ins(self, logins):
        "Add the total of log ins of a file to the batch summary"
        self.total_logins += logins

    def add_launches(self, launches):
        "Add the total of log ins of a file to the batch summary"
        self.total_launches += launches

    def add_entering(self, enterings):
        "Add the total of log ins of a file to the batch summary"
        self.total_enterings += enterings

    def add_exits(self, exits):
        "Add the total of exists of a file to the batch summary"
        self.total_exits += exits

    def add_accesses(self, accesses):
        "Add the total of accesses of a file to the batch summary"
        self.total_accesses += accesses

    def add_log_outs(self, logouts):
        "Add the total of log outs of a file to the batch summary"
        self.total_logouts += logouts

    def add_timeouts(self, timeouts):
        "Add the total of time outs of a file to the batch summary"
        self.total_timeouts += timeouts

    def add_rejects(self, rejects):
        "Add the total of rejects of a file to the batch summary"
        self.total_rejects += rejects

    def get_total_of_files(self):
        "Returns the total of files in the summary"
        return self.total_of_files

    def get_batch_start_date_time(self):
        "Returns the date/time when the batch started to be processed."
        return datetime.datetime.fromtimestamp(self.batch_start_date_time).isoformat()

    def set_batch_start_date_time(self):
        "Set the date/time when the batch started to be processed."
        self.batch_start_date_time = datetime.datetime.now().timestamp()

    def get_batch_end_date_time(self):
        "Returns the date/time when the batch finished processing"
        return datetime.datetime.fromtimestamp(self.batch_end_date_time).isoformat()

    def set_batch_end_date_time(self):
        "Set the date/time when the batch finished to be processed."
        self.batch_end_date_time = datetime.datetime.now().timestamp()

    def get_elapsed_process_time(self):
        "Returns the time elapsed to process the batch"
        elapsed_time = ''
        if not (self.batch_start_date_time is None) and not (self.batch_end_date_time is None):
            elapsed_time = self.batch_end_date_time - self.batch_start_date_time
        return str(timedelta(seconds=elapsed_time))