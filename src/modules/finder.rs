use walkdir::WalkDir;
use colored::Colorize;
use std::path::{PathBuf, Path};
use serde_json;
use serde::Deserialize;
use std::collections::HashMap;
use std::fs::File;
use zip::write::{FileOptions, ZipWriter};

#[derive(Debug)]
pub struct Finder {
    path: String,
    exts: Option<Vec<String>>,
    files_by_ext: Option<HashMap<String, Vec<PathBuf>>>,
    all: Option<Vec<PathBuf>>
}
#[derive(Deserialize)]
struct Extensions {
    audio: Vec<String>,
    compressed: Vec<String>,
    docs: Vec<String>,
    images: Vec<String>,
    video: Vec<String>,
    devs: Vec<String>,
    others: Vec<String>,
    user: Vec<String>
}
impl Finder {
    pub fn new(path: String, exts: String) -> Self {
        let current_ext;        
        let file = std::fs::read_to_string("modules/exts.json").unwrap_or_else(|_| {
            println!("{}: No se pudo cargar la base de datos", "Error Critico".red().bold());
            std::process::exit(1);
        });
        let json_file: Extensions = serde_json::from_str(&file).unwrap();
        if exts        == "audio".to_string() {
            current_ext = json_file.audio;

        } else if exts == "compressed".to_string() {
            current_ext = json_file.compressed;

        } else if exts == "docs".to_string() {
            current_ext = json_file.docs;

        } else if exts == "images".to_string() {
            current_ext = json_file.images;
        
        } else if exts == "video".to_string() {
            current_ext = json_file.video;

        } else if exts == "devs".to_string() {
            current_ext = json_file.devs;

        } else if exts == "others".to_string() {
            current_ext = json_file.others;
           
        } else if exts == "user".to_string() {
            current_ext = json_file.user;
        } else {
            println!("{}: Categoria de extension no disponible en la base de datos", "Error Critico".red().bold());
            std::process::exit(1);
        }
        Finder { path: path, exts: Some(current_ext), files_by_ext: Some(HashMap::new()), all: Some(vec![])}
    }

    pub fn find(&mut self) -> Result<HashMap<String, Vec<PathBuf>>, ()> {
        let mut files_by_ext: HashMap<String, Vec<PathBuf>> = HashMap::new();
        for entry in WalkDir::new(&self.path).into_iter().filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.starts_with(".") {
                continue;
            }
            if let Some(ext) = path.extension() {
                let ext = ext.to_string_lossy().to_string();
                if let Some(exts) = &self.exts {
                    if exts.iter().any(|e| e == &ext) {
                        files_by_ext.entry(ext).or_insert(vec![]).push(path.to_path_buf());
                        if let Some(all) = self.all.as_mut() {
                            all.push(path.to_path_buf());
                        }
                    }
                }
            }
        }
        if files_by_ext.is_empty() {
            return Err(());
        }
        Ok(files_by_ext)
    }
    
    pub fn filter(&mut self, keyword: &str) -> Vec<PathBuf> {
        let mut matches = vec![];
        if let Some(files) = self.all.as_ref() {
            for file in files {
                if let Some(file_name) = file.file_name() {
                    if file_name.to_string_lossy().contains(keyword) {
                        matches.push(file.clone());
                    }
                }
            }
        }
        return matches;
    }

    pub fn compress_files(&mut self, output_path: &Path) -> Result<(), Box<dyn std::error::Error>> {
        let file = File::create(output_path)?;
        let mut zip = ZipWriter::new(file);
        let options = FileOptions::default().compression_method(zip::CompressionMethod::Deflated);
    
        for (ext, files) in self.files_by_ext.clone().unwrap() {
            for file in files {
                if let Some(name) = file.file_name() {
                    let name = format!("{}-{}", ext, name.to_string_lossy());
                    zip.start_file(name, options)?;
                    let mut f = File::open(file)?;
                    std::io::copy(&mut f, &mut zip)?;
                }
            }
        }
    
        zip.finish()?;
        Ok(())
    }
}