use eframe::egui;
use std::path::PathBuf;
use std::sync::mpsc;
use std::thread;

use crate::extractor;

// 配色常量
const BG_PRIMARY: egui::Color32 = egui::Color32::from_rgb(18, 18, 24);
const BG_SECONDARY: egui::Color32 = egui::Color32::from_rgb(28, 28, 36);
const BG_TERTIARY: egui::Color32 = egui::Color32::from_rgb(38, 38, 48);
const ACCENT: egui::Color32 = egui::Color32::from_rgb(99, 102, 241);
const SUCCESS: egui::Color32 = egui::Color32::from_rgb(34, 197, 94);
const WARNING: egui::Color32 = egui::Color32::from_rgb(250, 204, 21);
const ERROR: egui::Color32 = egui::Color32::from_rgb(239, 68, 68);
const TEXT_PRIMARY: egui::Color32 = egui::Color32::from_rgb(248, 250, 252);
const TEXT_SECONDARY: egui::Color32 = egui::Color32::from_rgb(203, 213, 225);
const TEXT_MUTED: egui::Color32 = egui::Color32::from_rgb(148, 163, 184);
const BORDER: egui::Color32 = egui::Color32::from_rgb(51, 51, 64);

/// GUI应用状态
pub struct InvoiceApp {
    invoice_dir: String,
    buyer_keyword: String,
    output_path: String,
    log_messages: Vec<String>,
    is_processing: bool,
    status_message: String,
    result_receiver: Option<mpsc::Receiver<Result<String, String>>>,
    browse_dir_clicked: bool,
    browse_output_clicked: bool,
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
            browse_dir_clicked: false,
            browse_output_clicked: false,
        }
    }
}

impl InvoiceApp {
    pub fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        Self::default()
    }

    fn log(&mut self, message: String) {
        self.log_messages.push(message);
        if self.log_messages.len() > 100 {
            self.log_messages.remove(0);
        }
    }

    fn start_processing(&mut self) {
        if self.invoice_dir.is_empty() {
            self.log("[错误] 请选择发票目录".to_string());
            return;
        }

        if self.buyer_keyword.is_empty() {
            self.log("[错误] 请输入购买方关键词".to_string());
            return;
        }

        if self.output_path.is_empty() {
            self.output_path = format!("{}/发票清单.xlsx", self.invoice_dir);
        }

        self.is_processing = true;
        self.status_message = "正在处理...".to_string();
        self.log_messages.clear();

        let invoice_dir = self.invoice_dir.clone();
        let buyer_keyword = self.buyer_keyword.clone();
        let output_path = self.output_path.clone();

        self.log("━".repeat(50));
        self.log("[开始] 正在处理发票...".to_string());
        self.log(format!("[目录] {}", invoice_dir));
        self.log(format!("[关键词] {}", buyer_keyword));
        self.log(format!("[输出] {}", output_path));
        self.log("━".repeat(50));

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
                        self.log("━".repeat(50));
                        self.log("[完成] 发票处理成功!".to_string());
                        self.log(format!("[文件] {}", output_file));
                        self.log("━".repeat(50));
                        self.status_message = format!("处理完成: {}", output_file);
                    }
                    Err(e) => {
                        self.log(format!("[失败] {}", e));
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
        // 处理文件选择（在 UI 渲染之外）
        if self.browse_dir_clicked {
            self.browse_dir_clicked = false;
            if let Some(path) = rfd::FileDialog::new().pick_folder() {
                self.invoice_dir = path.to_string_lossy().to_string();
            }
        }
        
        if self.browse_output_clicked {
            self.browse_output_clicked = false;
            if let Some(path) = rfd::FileDialog::new()
                .set_file_name("发票清单.xlsx")
                .add_filter("Excel文件", &["xlsx"])
                .save_file()
            {
                self.output_path = path.to_string_lossy().to_string();
            }
        }

        if self.is_processing {
            self.check_result();
            ctx.request_repaint();
        }

        // 全局样式配置
        ctx.style_mut(|style| {
            style.visuals.dark_mode = true;
            style.visuals.panel_fill = BG_PRIMARY;
            style.visuals.window_fill = BG_SECONDARY;
            style.visuals.extreme_bg_color = BG_TERTIARY;
            
            style.visuals.widgets.inactive.bg_fill = BG_TERTIARY;
            style.visuals.widgets.inactive.bg_stroke = egui::Stroke::new(1.0, BORDER);
            style.visuals.widgets.inactive.rounding = egui::Rounding::same(6.0);
            
            style.visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(48, 48, 58);
            style.visuals.widgets.hovered.bg_stroke = egui::Stroke::new(1.0, ACCENT);
            
            style.visuals.widgets.active.bg_fill = BG_TERTIARY;
            style.visuals.widgets.active.bg_stroke = egui::Stroke::new(2.0, ACCENT);
            
            style.visuals.selection.bg_fill = ACCENT.linear_multiply(0.3);
            style.visuals.selection.stroke = egui::Stroke::new(1.0, ACCENT);
            
            style.spacing.item_spacing = egui::vec2(8.0, 8.0);
            style.spacing.button_padding = egui::vec2(16.0, 8.0);
        });

        egui::CentralPanel::default()
            .frame(egui::Frame::none()
                .fill(BG_PRIMARY)
                .inner_margin(egui::Margin::symmetric(24.0, 20.0)))
            .show(ctx, |ui| {
                // 标题区域
                ui.vertical_centered(|ui| {
                    ui.add_space(8.0);
                    ui.label(
                        egui::RichText::new("发票识别工具")
                            .size(28.0)
                            .color(TEXT_PRIMARY)
                            .strong()
                    );
                    ui.add_space(4.0);
                    ui.label(
                        egui::RichText::new("自动提取PDF发票信息，生成Excel清单")
                            .size(14.0)
                            .color(TEXT_MUTED)
                    );
                    ui.add_space(16.0);
                });

                // 配置卡片
                egui::Frame::none()
                    .fill(BG_SECONDARY)
                    .stroke(egui::Stroke::new(1.0, BORDER))
                    .rounding(egui::Rounding::same(12.0))
                    .inner_margin(egui::Margin::same(20.0))
                    .show(ui, |ui| {
                        ui.label(
                            egui::RichText::new("配置选项")
                                .size(16.0)
                                .color(TEXT_PRIMARY)
                                .strong()
                        );
                        ui.add_space(16.0);

                        // 发票目录
                        ui.horizontal(|ui| {
                            ui.label(
                                egui::RichText::new("发票目录")
                                    .size(14.0)
                                    .color(TEXT_SECONDARY)
                            );
                            ui.add_space(24.0);
                            
                            let text_edit = egui::TextEdit::singleline(&mut self.invoice_dir)
                                .desired_width(380.0)
                                .text_color(TEXT_PRIMARY);
                            ui.add(text_edit);
                            
                            ui.add_space(8.0);
                            let btn = egui::Button::new(
                                egui::RichText::new("选择文件夹").size(13.0).color(TEXT_PRIMARY)
                            )
                            .fill(BG_TERTIARY)
                            .rounding(egui::Rounding::same(6.0));
                            if ui.add(btn).clicked() {
                                self.browse_dir_clicked = true;
                            }
                        });
                        
                        ui.add_space(12.0);

                        // 购买方关键词
                        ui.horizontal(|ui| {
                            ui.label(
                                egui::RichText::new("购买方关键词")
                                    .size(14.0)
                                    .color(TEXT_SECONDARY)
                            );
                            ui.add_space(8.0);
                            
                            let text_edit = egui::TextEdit::singleline(&mut self.buyer_keyword)
                                .desired_width(380.0)
                                .text_color(TEXT_PRIMARY);
                            ui.add(text_edit);
                        });
                        
                        ui.add_space(12.0);

                        // 输出文件
                        ui.horizontal(|ui| {
                            ui.label(
                                egui::RichText::new("输出文件")
                                    .size(14.0)
                                    .color(TEXT_SECONDARY)
                            );
                            ui.add_space(24.0);
                            
                            let text_edit = egui::TextEdit::singleline(&mut self.output_path)
                                .desired_width(380.0)
                                .text_color(TEXT_PRIMARY);
                            ui.add(text_edit);
                            
                            ui.add_space(8.0);
                            let btn = egui::Button::new(
                                egui::RichText::new("选择位置").size(13.0).color(TEXT_PRIMARY)
                            )
                            .fill(BG_TERTIARY)
                            .rounding(egui::Rounding::same(6.0));
                            if ui.add(btn).clicked() {
                                self.browse_output_clicked = true;
                            }
                        });
                    });

                ui.add_space(16.0);

                // 日志卡片
                egui::Frame::none()
                    .fill(BG_SECONDARY)
                    .stroke(egui::Stroke::new(1.0, BORDER))
                    .rounding(egui::Rounding::same(12.0))
                    .inner_margin(egui::Margin::same(20.0))
                    .show(ui, |ui| {
                        ui.horizontal(|ui| {
                            ui.label(
                                egui::RichText::new("运行日志")
                                    .size(16.0)
                                    .color(TEXT_PRIMARY)
                                    .strong()
                            );
                            
                            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                if !self.log_messages.is_empty() {
                                    let clear_btn = egui::Button::new(
                                        egui::RichText::new("清除").size(12.0).color(TEXT_MUTED)
                                    )
                                    .fill(egui::Color32::TRANSPARENT)
                                    .stroke(egui::Stroke::new(1.0, BORDER));
                                    if ui.add(clear_btn).clicked() {
                                        self.log_messages.clear();
                                    }
                                }
                            });
                        });
                        ui.add_space(12.0);
                        
                        egui::Frame::none()
                            .fill(BG_PRIMARY)
                            .rounding(egui::Rounding::same(8.0))
                            .inner_margin(egui::Margin::same(12.0))
                            .show(ui, |ui| {
                                egui::ScrollArea::vertical()
                                    .max_height(180.0)
                                    .auto_shrink([false; 2])
                                    .stick_to_bottom(true)
                                    .show(ui, |ui| {
                                        ui.set_min_width(ui.available_width());
                                        
                                        if self.log_messages.is_empty() {
                                            ui.vertical_centered(|ui| {
                                                ui.add_space(50.0);
                                                ui.label(
                                                    egui::RichText::new("等待开始处理...")
                                                        .size(14.0)
                                                        .color(TEXT_MUTED)
                                                        .italics()
                                                );
                                            });
                                        } else {
                                            for msg in &self.log_messages {
                                                let color = if msg.contains("[完成]") || msg.contains("[成功]") {
                                                    SUCCESS
                                                } else if msg.contains("[错误]") || msg.contains("[失败]") {
                                                    ERROR
                                                } else if msg.contains("[开始]") {
                                                    ACCENT
                                                } else if msg.starts_with("━") {
                                                    TEXT_MUTED
                                                } else {
                                                    TEXT_SECONDARY
                                                };
                                                
                                                ui.label(
                                                    egui::RichText::new(msg.as_str())
                                                        .size(13.0)
                                                        .color(color)
                                                        .family(egui::FontFamily::Monospace)
                                                );
                                            }
                                        }
                                    });
                            });
                    });

                ui.add_space(20.0);

                // 底部操作栏
                ui.horizontal(|ui| {
                    // 状态指示器
                    let (status_color, status_icon) = if self.is_processing {
                        (WARNING, "●")
                    } else if self.status_message.contains("完成") {
                        (SUCCESS, "●")
                    } else if self.status_message.contains("失败") {
                        (ERROR, "●")
                    } else {
                        (TEXT_MUTED, "○")
                    };
                    
                    ui.label(
                        egui::RichText::new(status_icon)
                            .size(12.0)
                            .color(status_color)
                    );
                    ui.label(
                        egui::RichText::new(&self.status_message)
                            .size(14.0)
                            .color(TEXT_SECONDARY)
                    );

                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        let button_text = if self.is_processing {
                            "处理中..."
                        } else {
                            "开始识别"
                        };
                        
                        let button_color = if self.is_processing {
                            TEXT_MUTED
                        } else {
                            SUCCESS
                        };
                        
                        let button = egui::Button::new(
                            egui::RichText::new(button_text)
                                .size(15.0)
                                .color(egui::Color32::WHITE)
                                .strong()
                        )
                        .fill(button_color)
                        .rounding(egui::Rounding::same(8.0))
                        .min_size(egui::vec2(120.0, 42.0));
                        
                        if ui.add_enabled(!self.is_processing, button).clicked() {
                            self.start_processing();
                        }
                    });
                });
            });
    }
}
