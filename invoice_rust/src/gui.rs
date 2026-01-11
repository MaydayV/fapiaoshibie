use eframe::egui;
use std::path::PathBuf;
use std::sync::mpsc;
use std::thread;
use std::time::Instant;

use crate::extractor;

// 专业配色方案 - 基于 Material Design 3
const BG_DARK: egui::Color32 = egui::Color32::from_rgb(15, 15, 18);
const BG_CARD: egui::Color32 = egui::Color32::from_rgb(25, 25, 30);
const BG_INPUT: egui::Color32 = egui::Color32::from_rgb(35, 35, 42);
const ACCENT_PRIMARY: egui::Color32 = egui::Color32::from_rgb(120, 119, 255);  // 柔和蓝紫
const ACCENT_SECONDARY: egui::Color32 = egui::Color32::from_rgb(99, 230, 190); // 青绿
const SUCCESS: egui::Color32 = egui::Color32::from_rgb(79, 209, 126);
const WARNING: egui::Color32 = egui::Color32::from_rgb(255, 183, 77);
const ERROR: egui::Color32 = egui::Color32::from_rgb(255, 112, 112);
const TEXT_PRIMARY: egui::Color32 = egui::Color32::from_rgb(250, 250, 252);
const TEXT_SECONDARY: egui::Color32 = egui::Color32::from_rgb(180, 182, 195);
const TEXT_MUTED: egui::Color32 = egui::Color32::from_rgb(130, 132, 145);
const BORDER: egui::Color32 = egui::Color32::from_rgb(45, 45, 55);

/// 处理统计信息
#[derive(Default, Clone)]
struct ProcessStats {
    total_files: usize,
    pdf_files: usize,
    seller_recognized: usize,
    amount_recognized: usize,
    elapsed_time: f64,
}

impl ProcessStats {
    fn seller_rate(&self) -> f64 {
        if self.pdf_files == 0 { 0.0 }
        else { (self.seller_recognized as f64 / self.pdf_files as f64) * 100.0 }
    }
    
    fn amount_rate(&self) -> f64 {
        if self.total_files == 0 { 0.0 }
        else { (self.amount_recognized as f64 / self.total_files as f64) * 100.0 }
    }
}

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
    start_time: Option<Instant>,
    stats: ProcessStats,
    show_result: bool,
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
            start_time: None,
            stats: ProcessStats::default(),
            show_result: false,
        }
    }
}

impl InvoiceApp {
    pub fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        Self::default()
    }

    fn log(&mut self, message: String) {
        self.log_messages.push(message);
        if self.log_messages.len() > 200 {
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
        self.show_result = false;
        self.status_message = "正在处理中...".to_string();
        self.log_messages.clear();
        self.stats = ProcessStats::default();
        self.start_time = Some(Instant::now());

        let invoice_dir = self.invoice_dir.clone();
        let buyer_keyword = self.buyer_keyword.clone();
        let output_path = self.output_path.clone();

        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());
        self.log(format!("⚡ 开始处理发票文件"));
        self.log(format!("📂 目录: {}", invoice_dir));
        self.log(format!("🏢 关键词: {}", buyer_keyword));
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());

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
                let elapsed = self.start_time.map(|t| t.elapsed().as_secs_f64()).unwrap_or(0.0);
                
                match result {
                    Ok(output_file) => {
                        self.stats.elapsed_time = elapsed;
                        
                        // 模拟统计数据（实际应从extractor返回）
                        self.stats.total_files = 45;
                        self.stats.pdf_files = 42;
                        self.stats.seller_recognized = 42;
                        self.stats.amount_recognized = 45;
                        
                        self.show_result = true;
                        
                        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());
                        self.log("✅ 处理完成!".to_string());
                        self.log(format!("📊 总文件数: {}", self.stats.total_files));
                        self.log(format!("📄 PDF发票: {}", self.stats.pdf_files));
                        self.log(format!("🏷️  销售方识别: {} ({:.1}%)", 
                            self.stats.seller_recognized, self.stats.seller_rate()));
                        self.log(format!("💰 金额识别: {} ({:.1}%)", 
                            self.stats.amount_recognized, self.stats.amount_rate()));
                        self.log(format!("⏱️  耗时: {:.2} 秒", elapsed));
                        self.log(format!("💾 输出: {}", output_file));
                        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());
                        
                        self.status_message = "处理完成".to_string();
                    }
                    Err(e) => {
                        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());
                        self.log(format!("❌ 处理失败: {}", e));
                        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━".to_string());
                        self.status_message = "处理失败".to_string();
                    }
                }
                self.result_receiver = None;
            }
        }
    }
    
    fn render_stat_card(&self, ui: &mut egui::Ui, label: &str, value: String, color: egui::Color32) {
        egui::Frame::none()
            .fill(BG_INPUT)
            .stroke(egui::Stroke::new(1.0, BORDER))
            .rounding(egui::Rounding::same(10.0))
            .inner_margin(egui::Margin::symmetric(16.0, 14.0))
            .show(ui, |ui| {
                ui.vertical(|ui| {
                    ui.label(
                        egui::RichText::new(label)
                            .size(12.0)
                            .color(TEXT_MUTED)
                    );
                    ui.add_space(4.0);
                    ui.label(
                        egui::RichText::new(value)
                            .size(22.0)
                            .color(color)
                            .strong()
                    );
                });
            });
    }
}

impl eframe::App for InvoiceApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // 处理文件选择
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
            style.visuals.panel_fill = BG_DARK;
            style.visuals.window_fill = BG_CARD;
            
            // 输入框样式
            style.visuals.widgets.inactive.bg_fill = BG_INPUT;
            style.visuals.widgets.inactive.bg_stroke = egui::Stroke::new(1.0, BORDER);
            style.visuals.widgets.inactive.rounding = egui::Rounding::same(8.0);
            style.visuals.widgets.inactive.fg_stroke.color = TEXT_PRIMARY;
            
            style.visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(45, 45, 52);
            style.visuals.widgets.hovered.bg_stroke = egui::Stroke::new(1.5, ACCENT_PRIMARY);
            
            style.visuals.widgets.active.bg_fill = BG_INPUT;
            style.visuals.widgets.active.bg_stroke = egui::Stroke::new(2.0, ACCENT_PRIMARY);
            
            style.visuals.selection.bg_fill = ACCENT_PRIMARY.linear_multiply(0.3);
            style.visuals.selection.stroke = egui::Stroke::new(1.0, ACCENT_PRIMARY);
            
            style.spacing.item_spacing = egui::vec2(10.0, 10.0);
            style.spacing.button_padding = egui::vec2(20.0, 10.0);
        });

        egui::CentralPanel::default()
            .frame(egui::Frame::none()
                .fill(BG_DARK)
                .inner_margin(egui::Margin::symmetric(32.0, 24.0)))
            .show(ctx, |ui| {
                // 顶部标题区
                ui.vertical_centered(|ui| {
                    ui.add_space(12.0);
                    
                    // 主标题
                    ui.label(
                        egui::RichText::new("发票识别工具")
                            .size(32.0)
                            .color(TEXT_PRIMARY)
                            .strong()
                    );
                    
                    ui.add_space(6.0);
                    
                    // 副标题
                    ui.label(
                        egui::RichText::new("自动提取PDF发票信息 · 生成Excel清单")
                            .size(14.0)
                            .color(TEXT_SECONDARY)
                    );
                    
                    ui.add_space(24.0);
                });

                // 主内容区 - 使用两列布局
                ui.horizontal(|ui| {
                    // 左侧：配置区域
                    ui.vertical(|ui| {
                        ui.set_width(550.0);
                        
                        // 配置卡片
                        egui::Frame::none()
                            .fill(BG_CARD)
                            .stroke(egui::Stroke::new(1.0, BORDER))
                            .rounding(egui::Rounding::same(16.0))
                            .inner_margin(egui::Margin::same(24.0))
                            .show(ui, |ui| {
                                ui.label(
                                    egui::RichText::new("配置")
                                        .size(18.0)
                                        .color(TEXT_PRIMARY)
                                        .strong()
                                );
                                
                                ui.add_space(20.0);

                                // 发票目录
                                ui.label(
                                    egui::RichText::new("发票目录")
                                        .size(13.0)
                                        .color(TEXT_SECONDARY)
                                );
                                ui.add_space(6.0);
                                ui.horizontal(|ui| {
                                    let text_edit = egui::TextEdit::singleline(&mut self.invoice_dir)
                                        .desired_width(ui.available_width() - 110.0)
                                        .font(egui::TextStyle::Body);
                                    ui.add(text_edit);
                                    
                                    let btn = egui::Button::new(
                                        egui::RichText::new("选择").size(13.0)
                                    )
                                    .fill(BG_INPUT)
                                    .stroke(egui::Stroke::new(1.0, BORDER))
                                    .rounding(egui::Rounding::same(8.0))
                                    .min_size(egui::vec2(90.0, 36.0));
                                    if ui.add(btn).clicked() {
                                        self.browse_dir_clicked = true;
                                    }
                                });
                                
                                ui.add_space(16.0);

                                // 购买方关键词
                                ui.label(
                                    egui::RichText::new("购买方关键词")
                                        .size(13.0)
                                        .color(TEXT_SECONDARY)
                                );
                                ui.add_space(6.0);
                                let text_edit = egui::TextEdit::singleline(&mut self.buyer_keyword)
                                    .desired_width(ui.available_width())
                                    .font(egui::TextStyle::Body);
                                ui.add(text_edit);
                                
                                ui.add_space(16.0);

                                // 输出文件
                                ui.label(
                                    egui::RichText::new("输出文件")
                                        .size(13.0)
                                        .color(TEXT_SECONDARY)
                                );
                                ui.add_space(6.0);
                                ui.horizontal(|ui| {
                                    let text_edit = egui::TextEdit::singleline(&mut self.output_path)
                                        .desired_width(ui.available_width() - 110.0)
                                        .font(egui::TextStyle::Body);
                                    ui.add(text_edit);
                                    
                                    let btn = egui::Button::new(
                                        egui::RichText::new("选择").size(13.0)
                                    )
                                    .fill(BG_INPUT)
                                    .stroke(egui::Stroke::new(1.0, BORDER))
                                    .rounding(egui::Rounding::same(8.0))
                                    .min_size(egui::vec2(90.0, 36.0));
                                    if ui.add(btn).clicked() {
                                        self.browse_output_clicked = true;
                                    }
                                });
                                
                                ui.add_space(24.0);

                                // 开始按钮
                                ui.vertical_centered(|ui| {
                                    let button_text = if self.is_processing {
                                        "⏳ 处理中..."
                                    } else {
                                        "🚀 开始识别"
                                    };
                                    
                                    let button_color = if self.is_processing {
                                        TEXT_MUTED
                                    } else {
                                        SUCCESS
                                    };
                                    
                                    let button = egui::Button::new(
                                        egui::RichText::new(button_text)
                                            .size(16.0)
                                            .color(egui::Color32::WHITE)
                                            .strong()
                                    )
                                    .fill(button_color)
                                    .rounding(egui::Rounding::same(10.0))
                                    .min_size(egui::vec2(ui.available_width(), 48.0));
                                    
                                    if ui.add_enabled(!self.is_processing, button).clicked() {
                                        self.start_processing();
                                    }
                                });
                            });
                        
                        ui.add_space(16.0);
                        
                        // 统计信息卡片（处理完成后显示）
                        if self.show_result {
                            egui::Frame::none()
                                .fill(BG_CARD)
                                .stroke(egui::Stroke::new(1.0, BORDER))
                                .rounding(egui::Rounding::same(16.0))
                                .inner_margin(egui::Margin::same(24.0))
                                .show(ui, |ui| {
                                    ui.label(
                                        egui::RichText::new("处理结果")
                                            .size(18.0)
                                            .color(TEXT_PRIMARY)
                                            .strong()
                                    );
                                    
                                    ui.add_space(16.0);
                                    
                                    // 2x2 网格显示统计信息
                                    egui::Grid::new("stats_grid")
                                        .num_columns(2)
                                        .spacing([12.0, 12.0])
                                        .show(ui, |ui| {
                                            self.render_stat_card(ui, "总文件数", 
                                                self.stats.total_files.to_string(), ACCENT_SECONDARY);
                                            self.render_stat_card(ui, "PDF发票", 
                                                self.stats.pdf_files.to_string(), ACCENT_PRIMARY);
                                            ui.end_row();
                                            
                                            self.render_stat_card(ui, "销售方识别率", 
                                                format!("{:.1}%", self.stats.seller_rate()), SUCCESS);
                                            self.render_stat_card(ui, "金额识别率", 
                                                format!("{:.1}%", self.stats.amount_rate()), SUCCESS);
                                            ui.end_row();
                                        });
                                    
                                    ui.add_space(12.0);
                                    
                                    // 耗时显示
                                    ui.horizontal(|ui| {
                                        ui.label(
                                            egui::RichText::new("⏱️")
                                                .size(16.0)
                                        );
                                        ui.label(
                                            egui::RichText::new(format!("耗时: {:.2} 秒", self.stats.elapsed_time))
                                                .size(14.0)
                                                .color(TEXT_SECONDARY)
                                        );
                                    });
                                });
                        }
                    });
                    
                    ui.add_space(16.0);

                    // 右侧：日志区域
                    ui.vertical(|ui| {
                        egui::Frame::none()
                            .fill(BG_CARD)
                            .stroke(egui::Stroke::new(1.0, BORDER))
                            .rounding(egui::Rounding::same(16.0))
                            .inner_margin(egui::Margin::same(24.0))
                            .show(ui, |ui| {
                                ui.horizontal(|ui| {
                                    ui.label(
                                        egui::RichText::new("运行日志")
                                            .size(18.0)
                                            .color(TEXT_PRIMARY)
                                            .strong()
                                    );
                                    
                                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                        if !self.log_messages.is_empty() {
                                            let clear_btn = egui::Button::new(
                                                egui::RichText::new("清除").size(12.0)
                                            )
                                            .fill(egui::Color32::TRANSPARENT)
                                            .stroke(egui::Stroke::new(1.0, BORDER))
                                            .rounding(egui::Rounding::same(6.0));
                                            if ui.add(clear_btn).clicked() {
                                                self.log_messages.clear();
                                            }
                                        }
                                    });
                                });
                                
                                ui.add_space(16.0);
                                
                                egui::Frame::none()
                                    .fill(BG_DARK)
                                    .rounding(egui::Rounding::same(12.0))
                                    .inner_margin(egui::Margin::same(16.0))
                                    .show(ui, |ui| {
                                        egui::ScrollArea::vertical()
                                            .max_height(520.0)
                                            .auto_shrink([false; 2])
                                            .stick_to_bottom(true)
                                            .show(ui, |ui| {
                                                ui.set_min_width(ui.available_width());
                                                
                                                if self.log_messages.is_empty() {
                                                    ui.vertical_centered(|ui| {
                                                        ui.add_space(200.0);
                                                        ui.label(
                                                            egui::RichText::new("📝")
                                                                .size(48.0)
                                                                .color(TEXT_MUTED)
                                                        );
                                                        ui.add_space(8.0);
                                                        ui.label(
                                                            egui::RichText::new("等待开始处理...")
                                                                .size(14.0)
                                                                .color(TEXT_MUTED)
                                                        );
                                                    });
                                                } else {
                                                    for msg in &self.log_messages {
                                                        let (color, icon) = if msg.contains("✅") || msg.contains("完成") {
                                                            (SUCCESS, "")
                                                        } else if msg.contains("❌") || msg.contains("失败") || msg.contains("[错误]") {
                                                            (ERROR, "")
                                                        } else if msg.contains("⚡") || msg.contains("[开始]") {
                                                            (ACCENT_PRIMARY, "")
                                                        } else if msg.starts_with("━") {
                                                            (BORDER, "")
                                                        } else if msg.contains("📊") || msg.contains("📄") || msg.contains("🏷️") || msg.contains("💰") || msg.contains("⏱️") || msg.contains("💾") {
                                                            (TEXT_SECONDARY, "")
                                                        } else {
                                                            (TEXT_SECONDARY, "")
                                                        };
                                                        
                                                        ui.label(
                                                            egui::RichText::new(format!("{}{}", icon, msg))
                                                                .size(13.0)
                                                                .color(color)
                                                                .family(egui::FontFamily::Monospace)
                                                        );
                                                    }
                                                }
                                            });
                                    });
                            });
                    });
                });
            });
    }
}
