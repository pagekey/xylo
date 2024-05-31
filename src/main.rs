use structopt::StructOpt;


#[derive(StructOpt, Debug, PartialEq)]
#[structopt(name="xylo", about="Self-hosted app creation kit")]
enum Cli {
    New {
        project_name: String,
    }
}

trait ProjectHandler {
    fn handle(&self, cli: &Cli);
    fn handle_new(&self, project_name: &String);
}
struct DefaultProjectHandler;
impl ProjectHandler for DefaultProjectHandler {
    fn handle(&self, cli: &Cli) {
        match cli {
            Cli::New { project_name } => self.handle_new(project_name)
        }
    }
    fn handle_new(&self, project_name: &String) {
        println!("New project: {:?}", project_name);
    }
}

fn main() {
    let args = Cli::from_args();
    let handler = DefaultProjectHandler;
    handler.handle(&args);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_new() {
        let cli = Cli::from_iter(&["xylo", "new", "myproject"]);
        assert_eq!(cli, Cli::New { project_name: "myproject".into() });
    }
}
