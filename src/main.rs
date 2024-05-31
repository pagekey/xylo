use structopt::StructOpt;


#[derive(StructOpt, Debug, PartialEq)]
#[structopt(name="xylo", about="Self-hosted app creation kit")]
enum Cli {
    New {
        project_name: String,
    }
}

fn main() {
    let args = Cli::from_args();

    match args {
        Cli::New { project_name } => {
            println!("New project: {}", project_name);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_subcommand() {
        let cli = Cli::from_iter(&["xylo", "new", "myproject"]);
        assert_eq!(cli, Cli::New { project_name: "myproject".into() });
    }
}
