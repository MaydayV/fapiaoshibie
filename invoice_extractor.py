#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票信息提取脚本
功能：扫描目录中的所有PDF发票，提取发票号码、开票日期、购买方、销售方、金额等信息
输出：生成Excel格式的发票清单
"""

import fitz  # PyMuPDF
import os
import re
import time
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


def extract_invoice_info(pdf_path, buyer_keyword=None):
    """从PDF发票中提取信息

    Args:
        pdf_path: PDF文件路径
        buyer_keyword: 购买方公司名称关键词（用于识别购买方）
    """
    if buyer_keyword is None:
        buyer_keyword = ""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        info = {
            '发票号码': '',
            '开票日期': '',
            '购买方': '',
            '购买方税号': '',
            '销售方': '',
            '销售方税号': '',
            '项目内容': '',
            '金额': '',
            '备注': ''
        }

        # 提取发票号码 (20位纯数字)
        fp_match = re.search(r'\b(\d{20})\b', text)
        if fp_match:
            info['发票号码'] = fp_match.group(1)

        # 提取开票日期
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if date_match:
            info['开票日期'] = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

        # 提取税号（18位，可能包含字母）
        tax_numbers = re.findall(r'\b[0-9A-Z]{18}\b', text)
        valid_taxes = [t for t in tax_numbers if not (t.isdigit() and len(t) == 20)]
        if len(valid_taxes) >= 1:
            info['购买方税号'] = valid_taxes[0]
        if len(valid_taxes) >= 2:
            info['销售方税号'] = valid_taxes[1]

        # 提取项目内容
        item_match = re.search(r'\*([^*]+)\*', text)
        if item_match:
            info['项目内容'] = item_match.group(0)[:30]

        # 排除模式
        exclude_patterns = [
            r'\*[^*]+\*',
            r'项目|规格|单位|数量|单价|金额|税率|税额|合计|备注|开票人|下载次数|发票号码|开票日期',
            r'国家税务总局|发票监制|电子发票|普通发票|广东省税务局',
            r'价税合计|大写|小写',
        ]

        # 销售方关键词（扩展覆盖各种类型）
        seller_keywords = [
            '有限公司', '股份有限公司', '科技', '网络', '文化', '婴童',
            '贸易', '酒店', '饭店', '娱乐', '百货', '商店',
            '餐饮店', '饮食店', '加油站', '石油化工',
            '商行', '电子商务商行',
        ]

        # 提取所有可能的销售方名称
        all_sellers = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) < 5 or len(line) > 60:
                continue
            if any(re.search(p, line) for p in exclude_patterns):
                continue
            if any(kw in line for kw in seller_keywords):
                if not line.endswith('费'):
                    if line not in all_sellers:
                        all_sellers.append(line)

        # 识别购买方（根据传入的关键词匹配）
        if buyer_keyword:
            for c in all_sellers:
                if buyer_keyword in c:
                    info['购买方'] = c
                    break
        if not info['购买方'] and all_sellers:
            info['购买方'] = all_sellers[0]

        # 销售方是第二个不同的商家
        for c in all_sellers:
            if c != info['购买方']:
                info['销售方'] = c
                break

        # 如果没找到，尝试从税号附近提取
        if not info['销售方'] and info.get('销售方税号'):
            tax = info['销售方税号']
            idx = text.find(tax)
            if idx > 0:
                context = text[max(0, idx-100):min(len(text), idx+100)]
                for kw in ['店', '商行', '有限公司', '商贸', '科技', '贸易', '酒店', '饭店', '餐饮']:
                    match = re.search(r'([^\s\n]+{kw}[^\s\n]*)'.format(kw=kw), context)
                    if match:
                        seller = match.group(1).strip('*,、。.\n\t\r')
                        if seller != info['购买方'] and len(seller) > 4:
                            info['销售方'] = seller
                            break

        # 提取金额 - 优先找"圆整"后的金额
        amount_near_yuanzheng = re.search(r'圆整\s*[¥￥]?\s*([\d,]+\.?\d*)', text)
        if amount_near_yuanzheng:
            info['金额'] = amount_near_yuanzheng.group(1).replace(',', '')
        else:
            # 找所有¥后的金额，取最大的（价税合计通常是最大的）
            all_amounts = re.findall(r'[¥￥]\s*([\d,]+\.?\d*)', text)
            if all_amounts:
                amounts_float = []
                for a in all_amounts:
                    try:
                        amt = float(a.replace(',', ''))
                        if 0 < amt < 10000000:
                            amounts_float.append((amt, a))
                    except:
                        pass
                if amounts_float:
                    max_amount = max(amounts_float, key=lambda x: x[0])
                    info['金额'] = max_amount[1].replace(',', '')

        # 从文件名提取金额（备用方案）
        if not info['金额']:
            filename = os.path.basename(pdf_path)
            amount_match = re.search(r'(\d+\.?\d*)\.pdf', filename)
            if amount_match:
                info['金额'] = amount_match.group(1)

        return info

    except Exception as e:
        return {'备注': f'解析错误: {str(e)}'}


def process_invoices(base_path, buyer_keyword=None, output_path=None):
    """处理所有发票文件并生成Excel

    Args:
        base_path: 发票文件所在目录
        buyer_keyword: 购买方公司名称关键词（用于识别购买方）
        output_path: 输出Excel文件路径
    """
    # 记录开始时间
    start_time = time.time()
    all_invoices = []

    for root, dirs, files in os.walk(base_path):
        files = [f for f in files if not f.startswith('.')]
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, base_path)
                file_ext = os.path.splitext(file)[1].upper()

                invoice_data = {
                    '文件夹': rel_path,
                    '文件名': file,
                    '文件类型': file_ext
                }

                if file.lower().endswith('.pdf'):
                    info = extract_invoice_info(full_path, buyer_keyword)
                    invoice_data.update(info)

                all_invoices.append(invoice_data)

    all_invoices.sort(key=lambda x: (x['文件夹'], x['文件名']))

    # 从图片文件名提取金额
    for inv in all_invoices:
        if not inv.get('金额') and not inv['文件名'].endswith('.pdf'):
            amount_match = re.search(r'(\d+\.?\d*)\.(?:PNG|JPG|JPEG)', inv['文件名'])
            if amount_match:
                inv['金额'] = amount_match.group(1)

    # 生成Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "发票清单"

    headers = ['序号', '文件夹', '文件名', '发票号码', '开票日期', '购买方', '购买方税号',
               '销售方', '销售方税号', '项目内容', '金额', '备注']

    column_widths = [6, 26, 36, 18, 11, 22, 16, 28, 16, 18, 10, 12]
    for i, w in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64+i)].width = w

    header_font = Font(bold=True, size=10, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border

    for idx, inv in enumerate(all_invoices, 1):
        row = idx + 1
        ws.cell(row=row, column=1).value = idx
        ws.cell(row=row, column=2).value = inv['文件夹']
        ws.cell(row=row, column=3).value = inv['文件名']
        ws.cell(row=row, column=4).value = inv.get('发票号码', '')
        ws.cell(row=row, column=5).value = inv.get('开票日期', '')
        ws.cell(row=row, column=6).value = inv.get('购买方', '')
        ws.cell(row=row, column=7).value = inv.get('购买方税号', '')
        ws.cell(row=row, column=8).value = inv.get('销售方', '')
        ws.cell(row=row, column=9).value = inv.get('销售方税号', '')
        ws.cell(row=row, column=10).value = inv.get('项目内容', '')
        ws.cell(row=row, column=11).value = inv.get('金额', '')
        ws.cell(row=row, column=12).value = inv.get('备注', '')

        for col in range(1, 13):
            cell = ws.cell(row=row, column=col)
            cell.border = thin_border
            cell.alignment = Alignment(vertical='center')

    ws.freeze_panes = 'A2'

    if output_path is None:
        output_path = os.path.join(base_path, '发票清单.xlsx')

    wb.save(output_path)

    # 计算耗时
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计识别率
    pdf_count = sum(1 for inv in all_invoices if inv['文件名'].endswith('.pdf'))
    with_seller = sum(1 for inv in all_invoices if inv.get('销售方') and not inv['销售方'].startswith('*'))
    with_amount = sum(1 for inv in all_invoices if inv.get('金额'))

    print(f"发票识别完成！")
    print(f"  总文件数: {len(all_invoices)}")
    print(f"  PDF发票数: {pdf_count}")
    print(f"  销售方识别率: {with_seller/pdf_count*100:.1f}%")
    print(f"  金额识别率: {with_amount/len(all_invoices)*100:.1f}%")
    print(f"\n时间统计:")
    print(f"  总耗时: {total_time:.2f}秒")
    if len(all_invoices) > 0:
        avg_time = total_time / len(all_invoices)
        print(f"  平均每份: {avg_time:.3f}秒")
    print(f"\nExcel已保存: {output_path}")

    return output_path


if __name__ == "__main__":
    import sys

    # 获取发票目录
    if len(sys.argv) > 1:
        BASE_DIR = sys.argv[1]
    else:
        BASE_DIR = input("请输入发票文件所在目录路径: ").strip()

    # 获取购买方公司名称关键词
    if len(sys.argv) > 2:
        BUYER_KEYWORD = sys.argv[2]
    else:
        BUYER_KEYWORD = input("请输入购买方公司名称关键词（用于识别购买方）: ").strip()

    # 设置输出路径
    if len(sys.argv) > 3:
        OUTPUT_FILE = sys.argv[3]
    else:
        OUTPUT_FILE = os.path.join(BASE_DIR, '发票清单.xlsx')

    print(f"\n开始处理...")
    print(f"  发票目录: {BASE_DIR}")
    print(f"  购买方关键词: {BUYER_KEYWORD}")
    print(f"  输出文件: {OUTPUT_FILE}\n")

    process_invoices(BASE_DIR, BUYER_KEYWORD, OUTPUT_FILE)
