use std::process::Command;


pub trait SystemCaller {
    fn command_successful(&mut self, command: &str) -> bool;
}
struct ProductionSystemCaller;
impl SystemCaller for ProductionSystemCaller {
    fn command_successful(&mut self, command: &str) -> bool {
        let mut parts_iter = command.split_whitespace();
        let command_name: &str = parts_iter.next().expect("Failed to parse command.");
        let args: Vec<&str> = parts_iter.collect();
        let result = Command::new(command_name)
            .args(args)
            .output();
        match result {
            Ok(output) => output.status.success(),
            Err(_) => false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_command_successful_returns_true_for_successful_command() {
        assert_eq!(ProductionSystemCaller.command_successful("echo hi"), true);
    }
    #[test]
    fn test_command_successful_returns_false_for_failed_command() {
        assert_eq!(ProductionSystemCaller.command_successful("false"), false);
    }
    #[test]
    fn test_command_successful_returns_false_for_command_not_found() {
        assert_eq!(ProductionSystemCaller.command_successful("this-is-not-a-valid-command someargs"), false);
    }

    #[derive(Default)]
    struct FakeSystemCaller {
        calls: Vec<String>
    }
    impl SystemCaller for FakeSystemCaller {
        fn command_successful(&mut self, command: &str) -> bool {
            self.calls.push(command.to_string());
            true
        }
    }
    #[test]
    fn test_fake_system_caller_sets_last_call_properly() {
        let mut caller = FakeSystemCaller::default();
        assert_eq!(caller.calls.len(), 0);
        caller.command_successful("something");
        assert_eq!(caller.calls[0], "something");
    }
}
