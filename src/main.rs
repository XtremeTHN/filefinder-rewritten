mod modules {
    pub mod finder;
}

use modules::finder::Finder;
use std::env;
use structopt::StructOpt;
use colored::*;
#[derive(Debug, StructOpt, Clone)]
#[structopt(
    name = "Finder Files",
    about = "Busca archivos con diferentes extensiones, escrito en Rust"
)]
struct Opt {
    #[structopt(
        short = "f",
        long = "find",
        help = "Busca archivos especificando la categoria de extensiones que desees buscar"
    )]
    ext_opt: String,

    #[structopt(
        short = "p",
        long = "path",
        help = "Especifica la carpeta en donde buscar, por defecto es la carpeta actual de trabajo"
    )]
    path_opt: Option<String>,

    #[structopt(
        short = "s",
        long = "search",
        help = "Busca coincidencias entre los archivos encontrados"
    )]
    filter_opt: Option<String>,

    #[structopt(
        long = "no-formating",
        help = "Imprime los resultados sin formatear el texto"
    )]
    formater_opt: bool
}

fn main() {
    let mut opts = Opt::from_args();
    let opts_copy = opts.clone(); // Hacer una copia de opts
    if opts_copy.path_opt.unwrap_or_default() == "" {
        opts.path_opt = Some(env::current_dir().expect("No se pudo obtener la carpeta actual").display().to_string());
    }

    let mut finder_struct = Finder::new(opts.path_opt.clone().unwrap(), opts.ext_opt);
    let files = finder_struct.find();

    if opts.filter_opt.as_ref().unwrap_or(&"".to_string()) != "" {
        let coincidences = finder_struct.filter(opts.filter_opt.as_ref().unwrap());
        if !opts.formater_opt {
            println!("{} {}:", "Coincidencias de".purple(), opts.filter_opt.unwrap().blue());
            for x in coincidences {
                println!("      {}", x.display());
            }
            std::process::exit(0);
        } else {
            for x in coincidences {
                println!("{}", x.display());
            }
        }
    }

    match files {
        Ok(files) => {
            // Si se encontraron archivos, imprime sus rutas
            if !opts.formater_opt {
                for (ext, files) in files.clone() {
                    println!("{}: {}. {}:", "Extension".purple().bold(), ext.blue().bold(), "Archivos".purple().bold());
                    for x in files {
                        println!("      {}", x.display())
                    }
                }
            } else {
                for (_, x) in files {
                    for v in x {
                        println!("{}", v.display())
                    }
                }
            }
        }
        Err(_) => {
            // Si no se encontraron archivos, imprime un mensaje de error
            println!("No se encontraron archivos");
        }
    }
    //println!("{:?}",finder_struct.all.unwrap());
}