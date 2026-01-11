use eframe::egui;
use std::path::PathBuf;
use std::sync::mpsc;
use std::thread;

use crate::extractor;

/// GUI应用状态
pub struct InvoiceApp {
    invoice_dir: String,
    buyer_keyword: String,
    output_path: String,
    log_messages: Vec<String>,
    is_processing: bool,
    status_message: String,
    result_receiver: Option<mpsc::Receiver<Result<String, String>>>,
}

impl Default for InvoiceApp {
    fn default() -> Self {
        Self {
            invoice_dir: String::new(),
            buyer_keyword: String::new(),
            output_path: String::new(),
            log_messages: Vec::new(),
            is_processing: false,
            status_message: "就绪".to_string(),
            result_receiver: None,
        }
    }
}

impl InvoiceApp {
    pub fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        Self::default()
    }

    fn log(&mut self, message: String) {
        self.log_messages.push(message);
        // 限制日志条数
        if self.log_messages.len() > 100 {
            self.log_messages.remove(0);
        }
    }

    fn browse_directory(&mut self) {
        if let Some(path) = rfd::FileDialog::new().pick_folder() {
            self.invoice_dir = path.to_string_lossy().to_string();
        }
    }

    fn browse_output_file(&mut self) {
        if let Some(path) = rfd::FileDialog::new()
            .set_file_name("发票清单.xlsx")
            .add_filter("Excel文件", &["xlsx"])
            .save_file()
        {
            self.output_path = path.to_string_lossy().to_string();
        }
    }

    fn start_processing(&mut self) {
        if self.invoice_dir.is_empty() {
            self.log("错误: 请选择发票目录".to_string());
            return;
        }

        if self.buyer_keyword.is_empty() {
            self.log("错误: 请输入购买方关键词".to_string());
            return;
        }

        if self.output_path.is_empty() {
            self.output_path = format!("{}/发票清单.xlsx", self.invoice_dir);
        }

        self.is_processing = true;
        self.status_message = "处理中...".to_string();
        self.log_messages.clear();

        let invoice_dir = self.invoice_dir.clone();
        let buyer_keyword = self.buyer_keyword.clone();
        let output_path = self.output_path.clone();

        // 先记录日志
        self.log("=".repeat(50));
        self.log("开始处理发票...".to_string());
        self.log(format!("发票目录: {}", invoice_dir));
        self.log(format!("购买方关键词: {}", buyer_keyword));
        self.log(format!("输出文件: {}", output_path));
        self.log("=".repeat(50));

        let (tx, rx) = mpsc::channel();

        thread::spawn(move || {
            let base_path = PathBuf::from(&invoice_dir);
            let output_path_buf = PathBuf::from(&output_path);
            
            let buyer_kw = if buyer_keyword.is_empty() {
                None
            } else {
                Some(buyer_keyword.as_str())
            };

            let result = extractor::process_invoices(
                &base_path,
                buyer_kw,
                Some(&output_path_buf),
            );

            let _ = tx.send(result);
        });

        self.result_receiver = Some(rx);
    }

    fn check_result(&mut self) {
        if let Some(ref rx) = self.result_receiver {
            if let Ok(result) = rx.try_recv() {
                self.is_processing = false;
                match result {
                    Ok(output_file) => {
                        self.log("=".repeat(50));
                        self.log("✅ 处理完成！".to_string());
                        self.log(format!("📁 输出文件: {}", output_file));
                        self.log("=".repeat(50));
                        self.status_message = format!("处理完成 - {}", output_file);
                    }
                    Err(e) => {
                        self.log(format!("❌ 处理失败: {}", e));
                        self.status_message = format!("处理失败: {}", e);
                    }
                }
                self.result_receiver = None;
            }
        }
    }
}

impl eframe::App for InvoiceApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // 检查处理结果
        if self.is_processing {
            self.check_result();
            ctx.request_repaint();
        }

        // 设置整体样式
        ctx.style_mut(|style| {
            // 使用更现代的配色方案
            style.visuals.dark_mode = true;
            style.visuals.override_text_color = Some(egui::Color32::from_rgb(220, 220, 220));
            style.visuals.extreme_bg_color = egui::Color32::from_rgb(30, 30, 35);
            style.visuals.panel_fill = egui::Color32::from_rgb(40, 40, 45);
            style.visuals.window_fill = egui::Color32::from_rgb(35, 35, 40);
            style.visuals.widgets.noninteractive.bg_fill = egui::Color32::from_rgb(45, 45, 50);
            style.visuals.widgets.inactive.bg_fill = egui::Color32::from_rgb(50, 50, 55);
            style.visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(60, 60, 65);
            style.visuals.widgets.active.bg_fill = egui::Color32::from_rgb(70, 130, 200);
            style.visuals.widgets.open.bg_fill = egui::Color32::from_rgb(60, 100, 160);
            
            // 按钮样式
            style.visuals.widgets.active.weak_bg_fill = egui::Color32::from_rgb(46, 125, 50);
            style.visuals.widgets.hovered.weak_bg_fill = egui::Color32::from_rgb(56, 142, 60);
            
            // 间距优化
            style.spacing.item_spacing = egui::vec2(8.0, 6.0);
            style.spacing.button_padding = egui::vec2(12.0, 6.0);
            style.spacing.window_margin = egui::Margin::same(12.0);
        });

        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(egui::Color32::from_rgb(30, 30, 35)))
            .show(ctx, |ui| {
                ui.vertical_centered(|ui| {
                    ui.add_space(20.0);
                    
                    // 标题区域
                    ui.heading(
                        egui::RichText::new("📄 发票识别工具")
                            .size(24.0)
                            .color(egui::Color32::from_rgb(100, 150, 255))
                    );
                    ui.add_space(10.0);
                });

                ui.add_space(10.0);

                // 配置区域 - 使用卡片样式
                egui::Frame::group(ui.style())
                    .fill(egui::Color32::from_rgb(40, 40, 45))
                    .stroke(egui::Stroke::new(1.0, egui::Color32::from_rgb(60, 60, 65)))
                    .inner_margin(egui::Margin::same(12.0))
                    .show(ui, |ui| {
                        ui.vertical(|ui| {
                            ui.label(
                                egui::RichText::new("⚙️ 配置选项")
                                    .size(16.0)
                                    .color(egui::Color32::from_rgb(150, 200, 255))
                            );
                            ui.add_space(8.0);

                            // 发票目录
                            ui.horizontal(|ui| {
                                ui.label(
                                    egui::RichText::new("发票目录:")
                                        .color(egui::Color32::from_rgb(200, 200, 200))
                                );
                                ui.add_space(8.0);
                                ui.text_edit_singleline(&mut self.invoice_dir);
                                ui.add_space(8.0);
                                if ui
                                    .button(
                                        egui::RichText::new("📁 浏览...")
                                            .color(egui::Color32::WHITE)
                                    )
                                    .clicked()
                                {
                                    self.browse_directory();
                                }
                            });
                            ui.add_space(6.0);

                            // 购买方关键词
                            ui.horizontal(|ui| {
                                ui.label(
                                    egui::RichText::new("购买方关键词:")
                                        .color(egui::Color32::from_rgb(200, 200, 200))
                                );
                                ui.add_space(8.0);
                                ui.text_edit_singleline(&mut self.buyer_keyword);
                            });
                            ui.add_space(6.0);

                            // 输出文件
                            ui.horizontal(|ui| {
                                ui.label(
                                    egui::RichText::new("输出文件:")
                                        .color(egui::Color32::from_rgb(200, 200, 200))
                                );
                                ui.add_space(8.0);
                                ui.text_edit_singleline(&mut self.output_path);
                                ui.add_space(8.0);
                                if ui
                                    .button(
                                        egui::RichText::new("💾 浏览...")
                                            .color(egui::Color32::WHITE)
                                    )
                                    .clicked()
                                {
                                    self.browse_output_file();
                                }
                            });
                        });
                    });

                ui.add_space(12.0);

                // 日志区域 - 使用卡片样式
                egui::Frame::group(ui.style())
                    .fill(egui::Color32::from_rgb(40, 40, 45))
                    .stroke(egui::Stroke::new(1.0, egui::Color32::from_rgb(60, 60, 65)))
                    .inner_margin(egui::Margin::same(12.0))
                    .show(ui, |ui| {
                        ui.vertical(|ui| {
                            ui.label(
                                egui::RichText::new("📋 运行日志")
                                    .size(16.0)
                                    .color(egui::Color32::from_rgb(150, 200, 255))
                            );
                            ui.add_space(8.0);
                            
                            egui::Frame::none()
                                .fill(egui::Color32::from_rgb(25, 25, 30))
                                .inner_margin(egui::Margin::same(8.0))
                                .show(ui, |ui| {
                                    egui::ScrollArea::vertical()
                                        .max_height(250.0)
                                        .auto_shrink([false; 2])
                                        .show(ui, |ui| {
                                            if self.log_messages.is_empty() {
                                                ui.label(
                                                    egui::RichText::new("等待开始处理...")
                                                        .color(egui::Color32::from_rgb(150, 150, 150))
                                                        .italics()
                                                );
                                            } else {
                                                for msg in &self.log_messages {
                                                    ui.label(
                                                        egui::RichText::new(msg.as_str())
                                                            .color(egui::Color32::from_rgb(200, 200, 200))
                                                            .monospace()
                                                    );
                                                }
                                            }
                                        });
                                });
                        });
                    });

                ui.add_space(16.0);

                // 按钮区域
                ui.horizontal(|ui| {
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        let button_text = if self.is_processing {
                            "⏳ 处理中..."
                        } else {
                            "🚀 开始识别"
                        };
                        
                        let button = egui::Button::new(
                            egui::RichText::new(button_text)
                                .size(16.0)
                                .color(egui::Color32::WHITE)
                        )
                        .fill(if self.is_processing {
                            egui::Color32::from_rgb(100, 100, 100)
                        } else {
                            egui::Color32::from_rgb(46, 125, 50)
                        })
                        .min_size(egui::vec2(140.0, 40.0));
                        
                        if ui.add_enabled(!self.is_processing, button).clicked() {
                            self.start_processing();
                        }
                    });
                });

                ui.add_space(12.0);

                // 状态栏 - 使用卡片样式
                egui::Frame::group(ui.style())
                    .fill(egui::Color32::from_rgb(40, 40, 45))
                    .stroke(egui::Stroke::new(1.0, egui::Color32::from_rgb(60, 60, 65)))
                    .inner_margin(egui::Margin::same(10.0))
                    .show(ui, |ui| {
                        ui.horizontal(|ui| {
                            ui.label(
                                egui::RichText::new("状态:")
                                    .color(egui::Color32::from_rgb(150, 200, 255))
                            );
                            ui.add_space(8.0);
                            
                            let status_color = if self.is_processing {
                                egui::Color32::from_rgb(255, 193, 7)
                            } else if self.status_message.contains("完成") {
                                egui::Color32::from_rgb(76, 175, 80)
                            } else if self.status_message.contains("失败") {
                                egui::Color32::from_rgb(244, 67, 54)
                            } else {
                                egui::Color32::from_rgb(200, 200, 200)
                            };
                            
                            ui.label(
                                egui::RichText::new(&self.status_message)
                                    .color(status_color)
                            );
                        });
                    });
            });
    }
}
