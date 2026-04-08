// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

import './style.css';
import {
    GetDefaultPaperSize,
    GetDefaultTagLayout,
    GetDefaultTagTemplate,
    SaveProject,
    LoadProject,
    ImportCSV,
    SelectBackgroundImage,
    SavePDF,
    GetSystemFonts,
    ExportCSV,
    GetAppInfo
} from '../wailsjs/go/main/App';
import { PreviewRenderer } from './canvas';
import { LogInfo } from '../wailsjs/runtime/runtime';

const translations: any = {
    ko: {
        "CSV 가져오기": "CSV 가져오기",
        "스프레드시트": "스프레드시트",
        "프로젝트 열기": "프로젝트 열기",
        "프로젝트 저장": "프로젝트 저장",
        "PDF 저장": "PDF 저장",
        "용지 / 네임태그 설정": "용지 / 네임태그 설정",
        "텍스트 박스": "텍스트 박스",
        "속성": "속성",
        "라벨:": "라벨:",
        "폰트:": "폰트:",
        "크기:": "크기:",
        "정렬:": "정렬:",
        "색상:": "색상:",
        "왼쪽": "왼쪽",
        "중앙": "중앙",
        "오른쪽": "오른쪽",
        "전체 선택": "전체 선택",
        "전체 해제": "전체 해제",
        "적용": "적용",
        "취소": "취소",
        "배경 이미지": "배경 이미지",
        "배경 지우기": "배경 지우기",
        "인쇄 미리보기": "인쇄 미리보기",
        "미리보기": "미리보기",
        "단위:": "단위:",
        "용지:": "용지:",
        "사용자 정의": "사용자 정의",
        "용지 크기:": "용지 크기:",
        "태그 크기:": "태그 크기:",
        "열:": "열:",
        "행:": "행:",
        "여백X:": "여백 X:",
        "Y:": "Y:",
        "간격X:": "간격 X:",
        "너비:": "너비:",
        "높이:": "높이:",
        "줄간격:": "줄간격:",
        "자간:": "자간:",
        "배": "배",
        "스프레드시트 데이터 입력": "스프레드시트 데이터 입력",
        "SS_HINT": "엑셀이나 구글 시트에서 데이터를 복사(Ctrl+C)한 후, 아래 표에 붙여넣기(Ctrl+V) 하세요.",
        "+ 행 추가": "행 추가",
        "- 행 삭제": "행 삭제",
        "CSV 내보내기": "CSV 내보내기",
        "체크": "체크",
        "◀ 이전": "◀ 이전",
        "다음 ▶": "다음 ▶",
        "Fit": "맞춤",
        "선택된 데이터가 없습니다.": "선택된 데이터가 없습니다.",
        "PDF가 저장되었습니다:": "PDF가 저장되었습니다:",
        "정보": "정보"
    },
    en: {
        "CSV 가져오기": "Import CSV",
        "스프레드시트": "Spreadsheet",
        "프로젝트 열기": "Open Project",
        "프로젝트 저장": "Save Project",
        "PDF 저장": "Save PDF",
        "용지 / 네임태그 설정": "Paper / Tag Settings",
        "텍스트 박스": "Text Boxes",
        "속성": "Properties",
        "라벨:": "Label:",
        "폰트:": "Font:",
        "크기:": "Size:",
        "정렬:": "AL:",
        "색상:": "Color:",
        "왼쪽": "Left",
        "중앙": "Center",
        "오른쪽": "Right",
        "전체 선택": "Select All",
        "전체 해제": "Clear All",
        "적용": "Apply",
        "취소": "Cancel",
        "배경 이미지": "Background Image",
        "배경 지우기": "Clear Background",
        "인쇄 미리보기": "Print Preview",
        "미리보기": "Preview",
        "단위:": "Unit:",
        "용지:": "Paper:",
        "사용자 정의": "Custom",
        "용지 크기:": "Paper Size:",
        "태그 크기:": "Tag Size:",
        "열:": "Cols:",
        "행:": "Rows:",
        "여백X:": "Margin X:",
        "Y:": "Y:",
        "간격X:": "Gap X:",
        "너비:": "Width:",
        "높이:": "Height:",
        "줄간격:": "Line:",
        "자간:": "TR:",
        "배": "x",
        "스프레드시트 데이터 입력": "Spreadsheet Data Entry",
        "SS_HINT": "Copy data from Excel or Google Sheets (Ctrl+C) and paste it into the table below (Ctrl+V).",
        "+ 행 추가": "Add Row",
        "- 행 삭제": "Delete Row",
        "CSV 내보내기": "Export CSV",
        "체크": "Check",
        "◀ 이전": "◀ Prev",
        "다음 ▶": "Next ▶",
        "Fit": "Fit",
        "공통": "Common",
        "선택된 데이터가 없습니다.": "No data selected.",
        "PDF가 저장되었습니다:": "PDF saved to:",
        "정보": "About"
    }
};

let currentLang = localStorage.getItem('lang') || 'ko';

function tr(key: string) {
    const t = translations[currentLang];
    const res = (t && t[key]) || key;
    LogInfo(`tr called for ${key} -> ${res}`);
    return res;
}

function translateUI() {
    const t = translations[currentLang];
    document.querySelectorAll('[data-t]').forEach(el => {
        const key = el.getAttribute('data-t');
        if (key && t[key]) el.textContent = t[key];
    });

    document.querySelectorAll('[data-tooltip-key]').forEach(el => {
        const key = el.getAttribute('data-tooltip-key');
        const label = (key && t[key]) || key || '';
        if (!label) return;
        el.setAttribute('aria-label', label);
        el.setAttribute('data-tooltip', label);
    });
}

function showAlert(msg: string, duration: number = 3000) {
    const toast = document.getElementById('alert-toast');
    LogInfo(`showAlert: element found = ${!!toast}`);
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.remove('hidden');
    toast.style.opacity = '1';
    toast.style.display = 'block';
    LogInfo(`showAlert: displayed "${msg}", hidden=${toast.classList.contains('hidden')}`);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.style.display = 'none';
        }, 300);
    }, duration);
}

let renderer: PreviewRenderer;
let currentPaperSize: any;
let currentTagLayout: any;
let currentTagTemplate: any;
let currentEntries: any[] = [];
let commonValues: string[] = [];
let selectedTBIndex: number = -1;
let unitMode: 'mm' | 'inch' = 'mm';

const inchToMm = (inch: number) => inch * 25.4;

async function initApp() {
    try {
        currentPaperSize = await GetDefaultPaperSize();
        currentTagLayout = await GetDefaultTagLayout();
        currentTagTemplate = await GetDefaultTagTemplate();

        const fonts = await GetSystemFonts();
        populateFontDropdown(fonts);

        renderer = new PreviewRenderer('preview-canvas');

        updateUIFromState();
        setupEventListeners();
        setupIconPopovers();

        const langSelect = document.getElementById('lang-select') as HTMLSelectElement;
        if (langSelect) {
            langSelect.value = currentLang;
            langSelect.addEventListener('change', (e) => {
                currentLang = (e.target as HTMLSelectElement).value;
                localStorage.setItem('lang', currentLang);
                translateUI();
            });
        }
        translateUI();

        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);

    } catch (e) {
        console.error("Failed to initialize app:", e);
    }
}

function setupIconPopovers() {
    const popover = document.getElementById('icon-popover');
    if (!popover) return;

    let activeButton: HTMLElement | null = null;

    const hidePopover = () => {
        activeButton = null;
        popover.classList.add('hidden');
        popover.textContent = '';
    };

    const positionPopover = (target: HTMLElement) => {
        const rect = target.getBoundingClientRect();
        const popoverRect = popover.getBoundingClientRect();
        const left = rect.left + rect.width / 2 - popoverRect.width / 2;
        const top = rect.bottom + 12;
        const clampedLeft = Math.max(8, Math.min(left, window.innerWidth - popoverRect.width - 8));
        const clampedTop = Math.min(top, window.innerHeight - popoverRect.height - 8);

        popover.style.left = `${clampedLeft}px`;
        popover.style.top = `${clampedTop}px`;
    };

    const showPopover = (target: HTMLElement) => {
        const label = target.getAttribute('data-tooltip') || target.getAttribute('aria-label');
        if (!label) return;

        activeButton = target;
        popover.textContent = label;
        popover.classList.remove('hidden');
        positionPopover(target);
    };

    document.querySelectorAll<HTMLElement>('.icon-only-button[data-tooltip-key]').forEach(button => {
        button.addEventListener('mouseenter', () => showPopover(button));
        button.addEventListener('mouseleave', hidePopover);
        button.addEventListener('focus', () => showPopover(button));
        button.addEventListener('blur', hidePopover);
    });

    window.addEventListener('scroll', () => {
        if (activeButton) positionPopover(activeButton);
    }, true);

    window.addEventListener('resize', () => {
        if (activeButton) positionPopover(activeButton);
    });
}

function populateFontDropdown(fonts: any[]) {
    const select = document.getElementById('tb-font') as HTMLSelectElement;
    if (!select) return;
    select.innerHTML = '';

    // Remove existing dynamic font styles
    const oldStyle = document.getElementById('dynamic-fonts');
    if (oldStyle) oldStyle.remove();

    const style = document.createElement('style');
    style.id = 'dynamic-fonts';
    let css = '';

    fonts.forEach(font => {
        const family = font.Family || font;
        const path = font.Path;

        const opt = document.createElement('option');
        opt.value = family;
        opt.text = family;
        select.appendChild(opt);

        if (path) {
            // Register @font-face via the local-file handler
            const fontUrl = `/local-file${encodeURI(path)}`;
            // Use quotes for family name in case it contains spaces
            css += `
                @font-face {
                    font-family: "${family}";
                    src: url("${fontUrl}");
                }
            `;
        }
    });

    style.textContent = css;
    document.head.appendChild(style);

    // Redraw after fonts are loaded
    document.fonts.ready.then(() => {
        if (renderer) renderer.draw();
    });
}

function setupEventListeners() {
    // --- Global Actions ---
    document.getElementById('btn-save-project')?.addEventListener('click', async () => {
        const projectData: any = {
            version: 1, paper: currentPaperSize, layout: currentTagLayout,
            template: currentTagTemplate, entries: currentEntries, common_values: commonValues
        };
        try {
            const path = await SaveProject(projectData);
            if (path) console.log("Project saved to:", path);
        } catch (e) { console.error("Save failed:", e); }
    });

    document.getElementById('btn-save-pdf')?.addEventListener('click', async () => {
        try {
            console.log("Save PDF clicked. currentEntries:", currentEntries);
            if (!currentEntries || currentEntries.length === 0) {
                showAlert(tr("선택된 데이터가 없습니다."));
                return;
            }
            const checkedEntries = currentEntries.filter(e => e && e.checked);
            console.log("checkedEntries:", checkedEntries);
            if (checkedEntries.length === 0) {
                showAlert(tr("선택된 데이터가 없습니다."));
                return;
            }

            const projectData: any = {
                version: 1, paper: currentPaperSize, layout: currentTagLayout,
                template: currentTagTemplate, entries: currentEntries, common_values: commonValues
            };
            const path = await SavePDF(projectData);
            if (path) showAlert(`${tr("PDF가 저장되었습니다:")} ${path}`);
        } catch (err) {
            console.error("PDF Save failed:", err);
            showAlert("PDF Save failed: " + err);
        }
    });

    document.getElementById('btn-load-project')?.addEventListener('click', async () => {
        try {
            const data = await LoadProject();
            if (data) {
                currentPaperSize = data.paper; currentTagLayout = data.layout;
                currentTagTemplate = data.template; currentEntries = data.entries;
                commonValues = data.common_values;
                updateUIFromState();
                renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
            }
        } catch (e) { console.error("Load failed:", e); }
    });

    document.getElementById('btn-import-csv')?.addEventListener('click', async () => {
        try {
            const result: any = await ImportCSV();
            if (result && result.data) {
                currentEntries = result.data.map((row: string[]) => ({ checked: true, values: row }));
                showAlert(`CSV 데이터 ${currentEntries.length}건을 가져왔습니다.`);
            }
        } catch (e) { console.error("CSV Import failed:", e); }
    });

    document.getElementById('btn-about')?.addEventListener('click', async () => {
        try {
            const info = await GetAppInfo();
            document.getElementById('about-version')!.textContent = info.version || "1.0";
            document.getElementById('about-build-date')!.textContent = info.buildDate || "Unknown";
        } catch (e) {
            console.error("Failed to get app info", e);
        }
        document.getElementById('about-modal')?.classList.remove('hidden');
    });

    document.getElementById('btn-close-about')?.addEventListener('click', () => {
        document.getElementById('about-modal')?.classList.add('hidden');
    });

    document.getElementById('btn-spreadsheet')?.addEventListener('click', openSpreadsheet);
    document.getElementById('btn-preview')?.addEventListener('click', openPreview);
    document.getElementById('btn-close-preview')?.addEventListener('click', closePreview);
    document.getElementById('btn-prev-page')?.addEventListener('click', () => {
        if (previewCurrentPage > 0) {
            previewCurrentPage--;
            renderPreviewPage();
        }
    });
    document.getElementById('btn-next-page')?.addEventListener('click', () => {
        if (previewCurrentPage < previewTotalPages - 1) {
            previewCurrentPage++;
            renderPreviewPage();
        }
    });

    // --- Canvas Events ---
    window.addEventListener('tb-selected', (e: any) => {
        selectedTBIndex = e.detail.index;
        updateUIFromState();
    });

    window.addEventListener('tb-deselected', () => {
        selectedTBIndex = -1;
        updateUIFromState();
        renderer.draw();
    });

    window.addEventListener('tb-moved', (e: any) => {
        if (selectedTBIndex === e.detail.index) {
            (document.getElementById('tb-x') as HTMLInputElement).value = formatVal(e.detail.x);
            (document.getElementById('tb-y') as HTMLInputElement).value = formatVal(e.detail.y);
            if (e.detail.w !== undefined) (document.getElementById('tb-w') as HTMLInputElement).value = formatVal(e.detail.w);
            if (e.detail.h !== undefined) (document.getElementById('tb-h') as HTMLInputElement).value = formatVal(e.detail.h);
        }
    });

    // --- Zoom Controls ---
    document.getElementById('btn-zoom-fit')?.addEventListener('click', () => { renderer.setZoom('fit'); updateUIFromState(); });
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => { renderer.setZoom('out'); updateUIFromState(); });
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => { renderer.setZoom('in'); updateUIFromState(); });
    document.getElementById('btn-zoom-100')?.addEventListener('click', () => { renderer.setZoom('100'); updateUIFromState(); });

    // Handle window resize to auto-fit canvas
    window.addEventListener('resize', () => {
        if (renderer) {
            renderer.draw();
            updateUIFromState();
        }
    });

    // --- Unit Toggle ---
    document.getElementsByName('unit')?.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const newMode = (e.target as HTMLInputElement).value as 'mm' | 'inch';
            if (newMode === unitMode) return;
            unitMode = newMode;
            updateUIFromState();
        });
    });

    // --- Background Image ---
    document.getElementById('btn-select-bg')?.addEventListener('click', async () => {
        const path = await SelectBackgroundImage();
        if (path) {
            currentTagTemplate.background_image = path;
            updateUIFromState();
            renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
        }
    });

    document.getElementById('btn-clear-bg')?.addEventListener('click', () => {
        currentTagTemplate.background_image = "";
        updateUIFromState();
        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
    });

    // --- Paper Settings ---
    document.getElementById('paper-preset')?.addEventListener('change', (e) => {
        const val = (e.target as HTMLSelectElement).value;
        currentPaperSize.name = val;
        if (val === 'A4') { currentPaperSize.width_mm = 210; currentPaperSize.height_mm = 297; }
        else if (val === 'A3') { currentPaperSize.width_mm = 297; currentPaperSize.height_mm = 420; }
        updateUIFromState();
        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
    });

    ['paper-width', 'paper-height'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', (e) => {
            const val = parseFloat((e.target as HTMLInputElement).value);
            const mmVal = unitMode === 'inch' ? inchToMm(val) : val;
            if (id === 'paper-width') currentPaperSize.width_mm = mmVal;
            else currentPaperSize.height_mm = mmVal;
            currentPaperSize.name = 'Custom';
            (document.getElementById('paper-preset') as HTMLSelectElement).value = 'Custom';
            renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
        });
    });

    // --- Layout Settings ---
    const layoutKeyMap: any = {
        'tag-width': 'tag_width_mm', 'tag-height': 'tag_height_mm',
        'cols': 'columns', 'rows': 'rows',
        'offset-x': 'offset_x_mm', 'offset-y': 'offset_y_mm',
        'gap-x': 'gap_x_mm', 'gap-y': 'gap_y_mm'
    };
    Object.keys(layoutKeyMap).forEach(id => {
        document.getElementById(id)?.addEventListener('input', (e) => {
            const val = parseFloat((e.target as HTMLInputElement).value);
            const actualKey = layoutKeyMap[id];
            if (id === 'cols' || id === 'rows') {
                currentTagLayout[actualKey] = Math.floor(val);
            } else {
                currentTagLayout[actualKey] = unitMode === 'inch' ? inchToMm(val) : val;
            }
            renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
        });
    });

    // --- TextBox Management ---
    document.getElementById('btn-add-tb')?.addEventListener('click', () => {
        const newTB = {
            label: "새 텍스트", x_mm: 5.0, y_mm: 5.0 + currentTagTemplate.text_boxes.length * 10,
            width_mm: 80.0, height_mm: 10.0, font_family: "Arial", font_size: 12,
            alignment: "center", color: "#000000", bold: false, italic: false,
            line_spacing: 1.0, letter_spacing: 0.0
        };
        currentTagTemplate.text_boxes.push(newTB);
        selectedTBIndex = currentTagTemplate.text_boxes.length - 1;
        updateUIFromState();
        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
    });

    document.getElementById('btn-del-tb')?.addEventListener('click', () => {
        if (selectedTBIndex >= 0) {
            currentTagTemplate.text_boxes.splice(selectedTBIndex, 1);
            selectedTBIndex = currentTagTemplate.text_boxes.length > 0 ? 0 : -1;
            updateUIFromState();
            renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
        }
    });

    document.getElementById('btn-up-tb')?.addEventListener('click', () => {
        if (selectedTBIndex <= 0) return;
        const box = currentTagTemplate.text_boxes.splice(selectedTBIndex, 1)[0];
        currentTagTemplate.text_boxes.splice(selectedTBIndex - 1, 0, box);
        selectedTBIndex--;
        updateUIFromState();
        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
    });

    document.getElementById('btn-down-tb')?.addEventListener('click', () => {
        if (selectedTBIndex < 0 || selectedTBIndex >= currentTagTemplate.text_boxes.length - 1) return;
        const box = currentTagTemplate.text_boxes.splice(selectedTBIndex, 1)[0];
        currentTagTemplate.text_boxes.splice(selectedTBIndex + 1, 0, box);
        selectedTBIndex++;
        updateUIFromState();
        renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
    });

    document.getElementById('textbox-list')?.addEventListener('change', (e) => {
        selectedTBIndex = parseInt((e.target as HTMLSelectElement).value);
        if (selectedTBIndex >= 0) loadTextBoxProps(currentTagTemplate.text_boxes[selectedTBIndex]);
    });

    // --- TextBox Property Listeners ---
    const tbInputs = ['tb-label', 'tb-x', 'tb-y', 'tb-w', 'tb-h', 'tb-size', 'tb-font', 'tb-align', 'tb-line', 'tb-letter', 'tb-color', 'tb-bold', 'tb-italic'];
    tbInputs.forEach(id => {
        const el = document.getElementById(id);
        const handler = (e: Event) => updateSelectedTB(id, e);
        el?.addEventListener('change', handler);
        el?.addEventListener('input', handler);
    });
}


function formatVal(val: number) {
    if (unitMode === 'inch') return (val / 25.4).toFixed(3);
    return val.toFixed(1);
}

function updateSelectedTB(id: string, e: Event) {
    if (selectedTBIndex < 0) return;
    const tb = currentTagTemplate.text_boxes[selectedTBIndex];
    const target = e.target as any;

    switch (id) {
        case 'tb-label':
            tb.label = target.value;
            const opt = (document.getElementById('textbox-list') as HTMLSelectElement).options[selectedTBIndex];
            if (opt) opt.text = `${selectedTBIndex + 1}. ${tb.label}`;
            break;
        case 'tb-x': tb.x_mm = unitMode === 'inch' ? inchToMm(parseFloat(target.value)) : parseFloat(target.value); break;
        case 'tb-y': tb.y_mm = unitMode === 'inch' ? inchToMm(parseFloat(target.value)) : parseFloat(target.value); break;
        case 'tb-w': tb.width_mm = unitMode === 'inch' ? inchToMm(parseFloat(target.value)) : parseFloat(target.value); break;
        case 'tb-h': tb.height_mm = unitMode === 'inch' ? inchToMm(parseFloat(target.value)) : parseFloat(target.value); break;
        case 'tb-size': tb.font_size = parseFloat(target.value); break;
        case 'tb-font':
            tb.font_family = target.value;
            // Explicitly load the font before redrawing
            document.fonts.load(`12px "${target.value}"`).then(() => {
                renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
            });
            return; // skip the sync updateData below
        case 'tb-align': tb.alignment = target.value; break;
        case 'tb-line': tb.line_spacing = parseFloat(target.value); break;
        case 'tb-letter': tb.letter_spacing = parseFloat(target.value); break;
        case 'tb-color': tb.color = target.value; break;
        case 'tb-bold': tb.bold = target.checked; break;
        case 'tb-italic': tb.italic = target.checked; break;
    }
    renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate);
}

function updateUIFromState() {
    const unitLabel = unitMode === 'inch' ? 'in' : 'mm';
    document.querySelectorAll('.unit-label').forEach(el => el.textContent = unitLabel);

    const bgDisplay = document.getElementById('bg-path-display');
    if (bgDisplay) bgDisplay.textContent = currentTagTemplate.background_image || '없음';

    (document.getElementById('paper-preset') as HTMLSelectElement).value = currentPaperSize.name;
    (document.getElementById('paper-width') as HTMLInputElement).value = formatVal(currentPaperSize.width_mm);
    (document.getElementById('paper-height') as HTMLInputElement).value = formatVal(currentPaperSize.height_mm);

    (document.getElementById('tag-width') as HTMLInputElement).value = formatVal(currentTagLayout.tag_width_mm);
    (document.getElementById('tag-height') as HTMLInputElement).value = formatVal(currentTagLayout.tag_height_mm);
    (document.getElementById('cols') as HTMLInputElement).value = currentTagLayout.columns.toString();
    (document.getElementById('rows') as HTMLInputElement).value = currentTagLayout.rows.toString();
    (document.getElementById('offset-x') as HTMLInputElement).value = formatVal(currentTagLayout.offset_x_mm);
    (document.getElementById('offset-y') as HTMLInputElement).value = formatVal(currentTagLayout.offset_y_mm);
    (document.getElementById('gap-x') as HTMLInputElement).value = formatVal(currentTagLayout.gap_x_mm);
    (document.getElementById('gap-y') as HTMLInputElement).value = formatVal(currentTagLayout.gap_y_mm);

    const listEl = document.getElementById('textbox-list') as HTMLSelectElement;
    listEl.innerHTML = '';
    currentTagTemplate.text_boxes.forEach((tb: any, i: number) => {
        const opt = document.createElement('option');
        opt.value = i.toString();
        opt.text = `${i + 1}. ${tb.label}`;
        listEl.appendChild(opt);
    });

    if (selectedTBIndex >= 0 && selectedTBIndex < currentTagTemplate.text_boxes.length) {
        listEl.selectedIndex = selectedTBIndex;
        loadTextBoxProps(currentTagTemplate.text_boxes[selectedTBIndex]);
    }

    const zoomLabel = document.getElementById('zoom-label');
    if (zoomLabel && renderer) {
        zoomLabel.textContent = `${renderer.getScalePercentage()}%`;
    }
}

function loadTextBoxProps(tb: any) {
    (document.getElementById('tb-label') as HTMLInputElement).value = tb.label;
    (document.getElementById('tb-x') as HTMLInputElement).value = formatVal(tb.x_mm);
    (document.getElementById('tb-y') as HTMLInputElement).value = formatVal(tb.y_mm);
    (document.getElementById('tb-w') as HTMLInputElement).value = formatVal(tb.width_mm);
    (document.getElementById('tb-h') as HTMLInputElement).value = formatVal(tb.height_mm);
    (document.getElementById('tb-size') as HTMLInputElement).value = tb.font_size.toString();
    (document.getElementById('tb-font') as HTMLSelectElement).value = tb.font_family;
    (document.getElementById('tb-align') as HTMLSelectElement).value = tb.alignment;
    (document.getElementById('tb-line') as HTMLInputElement).value = tb.line_spacing.toString();
    (document.getElementById('tb-letter') as HTMLInputElement).value = tb.letter_spacing.toString();
    (document.getElementById('tb-color') as HTMLInputElement).value = tb.color;
    (document.getElementById('tb-bold') as HTMLInputElement).checked = tb.bold;
    (document.getElementById('tb-italic') as HTMLInputElement).checked = tb.italic;
}

// --- Spreadsheet Functions ---
function openSpreadsheet() {
    document.getElementById('spreadsheet-modal')?.classList.remove('hidden');
    populateSpreadsheet();
}

function closeSpreadsheet() {
    document.getElementById('spreadsheet-modal')?.classList.add('hidden');
}

function populateSpreadsheet() {
    const headerRow = document.getElementById('ss-header-row')!;
    const body = document.getElementById('ss-body')!;

    // Header
    headerRow.innerHTML = `<th style="width: 40px;" data-t="체크">${tr("체크")}</th><th style="width: 40px;">#</th>`;
    currentTagTemplate.text_boxes.forEach((tb: any) => {
        const th = document.createElement('th');
        th.textContent = tb.label;
        headerRow.appendChild(th);
    });

    body.innerHTML = '';

    // Common Values Row (Index 0)
    const commonTr = document.createElement('tr');
    commonTr.className = 'common-row';
    let commonHtml = `<td></td><td class="ss-row-num" data-t="공통">${tr("공통")}</td>`;
    currentTagTemplate.text_boxes.forEach((_: any, colIdx: number) => {
        const val = commonValues[colIdx] || '';
        commonHtml += `<td><input type="text" value="${val}" data-col="${colIdx}" class="ss-common-input"></td>`;
    });
    commonTr.innerHTML = commonHtml;
    body.appendChild(commonTr);

    // Data Entries
    currentEntries.forEach((entry, rowIdx) => {
        const tr = document.createElement('tr');
        tr.dataset.row = rowIdx.toString();
        let html = `<td><input type="checkbox" ${entry.checked ? 'checked' : ''} class="ss-row-check"></td>`;
        html += `<td class="ss-row-num">${rowIdx + 1}</td>`;
        currentTagTemplate.text_boxes.forEach((_: any, colIdx: number) => {
            html += `<td><input type="text" value="${entry.values[colIdx] || ''}" data-col="${colIdx}"></td>`;
        });
        tr.innerHTML = html;
        body.appendChild(tr);
    });

    if (currentEntries.length === 0) addSpreadsheetRow();
    setupSpreadsheetListeners();
}

function setupSpreadsheetListeners() {
    document.getElementById('btn-close-spreadsheet')?.addEventListener('click', closeSpreadsheet);
    document.getElementById('btn-ss-cancel')?.addEventListener('click', closeSpreadsheet);
    document.getElementById('btn-ss-apply')?.addEventListener('click', () => { applySpreadsheet(); closeSpreadsheet(); renderer.updateData(currentPaperSize, currentTagLayout, currentTagTemplate); });

    const addBtn = document.getElementById('btn-ss-add-row');
    if (addBtn) addBtn.onclick = addSpreadsheetRow;
    const delBtn = document.getElementById('btn-ss-del-row');
    if (delBtn) delBtn.onclick = deleteSpreadsheetRow;

    document.getElementById('btn-ss-export')?.addEventListener('click', async () => {
        applySpreadsheet();
        const headers = ["Checked"];
        currentTagTemplate.text_boxes.forEach((tb: any) => headers.push(tb.label));
        const data = currentEntries.map(e => [e.checked ? "YES" : "NO", ...e.values]);
        // Add common values as a special row if needed, but usually just entries
        const path = await ExportCSV(headers, data);
        if (path) showAlert(`Exported to: ${path}`);
    });

    const selectAll = document.getElementById('btn-ss-select-all');
    if (selectAll) selectAll.onclick = () => document.querySelectorAll('.ss-row-check').forEach((el: any) => el.checked = true);
    const clearAll = document.getElementById('btn-ss-clear-all');
    if (clearAll) clearAll.onclick = () => document.querySelectorAll('.ss-row-check').forEach((el: any) => el.checked = false);

    const ssTable = document.getElementById('spreadsheet-table');
    if (ssTable) ssTable.onpaste = (e: any) => handleSpreadsheetPaste(e);
}

function addSpreadsheetRow() {
    const body = document.getElementById('ss-body')!;
    const tr = document.createElement('tr');
    const rowIdx = Array.from(body.children).filter(el => !el.classList.contains('common-row')).length;
    tr.dataset.row = rowIdx.toString();
    let html = `<td><input type="checkbox" checked class="ss-row-check"></td>`;
    html += `<td class="ss-row-num">${rowIdx + 1}</td>`;
    currentTagTemplate.text_boxes.forEach((_: any, colIdx: number) => {
        html += `<td><input type="text" value="" data-col="${colIdx}"></td>`;
    });
    tr.innerHTML = html;
    body.appendChild(tr);
}

function deleteSpreadsheetRow() {
    const body = document.getElementById('ss-body')!;
    if (body.lastElementChild) body.removeChild(body.lastElementChild);
}

function handleSpreadsheetPaste(e: ClipboardEvent) {
    e.preventDefault();
    const text = e.clipboardData?.getData('text');
    if (!text) return;
    const rows = text.split('\n').filter(r => r.trim() !== '').map(r => r.split('\t'));
    const body = document.getElementById('ss-body')!;
    rows.forEach((row, rowIdx) => {
        const tr = document.createElement('tr');
        const startIdx = Array.from(body.children).filter(el => !el.classList.contains('common-row')).length;
        tr.dataset.row = (startIdx + rowIdx).toString();
        let html = `<td><input type="checkbox" checked class="ss-row-check"></td>`;
        html += `<td class="ss-row-num">${startIdx + rowIdx + 1}</td>`;
        currentTagTemplate.text_boxes.forEach((_: any, colIdx: number) => {
            html += `<td><input type="text" value="${row[colIdx] || ''}" data-col="${colIdx}"></td>`;
        });
        tr.innerHTML = html;
        body.appendChild(tr);
    });
}

function applySpreadsheet() {
    const body = document.getElementById('ss-body')!;

    // Extract Common Values
    const commonValuesRow = body.querySelector('.common-row');
    if (commonValuesRow) {
        const commonInputs = Array.from(commonValuesRow.querySelectorAll('.ss-common-input')) as HTMLInputElement[];
        commonValues = commonInputs.map(input => input.value);
    }

    // Extract Data Entries
    const newEntries: any[] = [];
    Array.from(body.children).forEach(tr => {
        if (tr.classList.contains('common-row')) return;
        const checkbox = tr.querySelector('.ss-row-check') as HTMLInputElement;
        const textInputs = Array.from(tr.querySelectorAll('input[type="text"]:not(.ss-common-input)')) as HTMLInputElement[];
        newEntries.push({
            checked: checkbox.checked,
            values: textInputs.sort((a, b) => {
                const colA = parseInt(a.getAttribute('data-col') || '0');
                const colB = parseInt(b.getAttribute('data-col') || '0');
                return colA - colB;
            }).map(input => input.value)
        });
    });
    currentEntries = newEntries;
}

let previewCurrentPage = 0;
let previewTotalPages = 1;

function openPreview() {
    try {
        LogInfo("openPreview startup");
        console.log("openPreview called. currentEntries:", currentEntries);
        LogInfo(`currentEntries count: ${currentEntries ? currentEntries.length : 'null/undefined'}`);

        if (!currentEntries || currentEntries.length === 0) {
            const msg = tr("선택된 데이터가 없습니다.");
            LogInfo(`Empty entries. Alerting: ${msg}`);
            showAlert(msg);
            return;
        }
        const checkedEntries = currentEntries.filter(e => e && e.checked);
        LogInfo(`checkedEntries count: ${checkedEntries.length}`);

        if (checkedEntries.length === 0) {
            const msg = tr("선택된 데이터가 없습니다.");
            LogInfo(`No checked entries. Alerting: ${msg}`);
            showAlert(msg);
            return;
        }
        const tagsPerPage = currentTagLayout.columns * currentTagLayout.rows;
        previewTotalPages = Math.ceil(checkedEntries.length / tagsPerPage);
        if (previewTotalPages === 0) previewTotalPages = 1;
        previewCurrentPage = 0;

        LogInfo("Showing preview modal");
        document.getElementById('preview-modal')?.classList.remove('hidden');
        renderPreviewPage();
    } catch (err) {
        LogInfo(`Error in openPreview: ${err}`);
        console.error("Error in openPreview:", err);
        showAlert("Error opening preview: " + err);
    }
}

function closePreview() {
    document.getElementById('preview-modal')?.classList.add('hidden');
}

function renderPreviewPage() {
    const pageLabel = document.getElementById('preview-page-label');
    if (pageLabel) pageLabel.textContent = `${previewCurrentPage + 1} / ${previewTotalPages}`;

    const canvas = document.getElementById('print-preview-canvas') as HTMLCanvasElement;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const checkedEntries = currentEntries.filter(e => e.checked);
    const tagsPerPage = currentTagLayout.columns * currentTagLayout.rows;
    const startIndex = previewCurrentPage * tagsPerPage;

    const scale = 2.5;

    canvas.width = currentPaperSize.width_mm * scale;
    canvas.height = currentPaperSize.height_mm * scale;

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const tagWPx = currentTagLayout.tag_width_mm * scale;
    const tagHPx = currentTagLayout.tag_height_mm * scale;
    const gapXPx = currentTagLayout.gap_x_mm * scale;
    const gapYPx = currentTagLayout.gap_y_mm * scale;
    const offXPx = currentTagLayout.offset_x_mm * scale;
    const offYPx = currentTagLayout.offset_y_mm * scale;

    const drawContent = (bgImg: HTMLImageElement | null) => {
        for (let pos = 0; pos < tagsPerPage; pos++) {
            const entryIdx = startIndex + pos;
            if (entryIdx >= checkedEntries.length) break;

            const entry = checkedEntries[entryIdx];
            const c = pos % currentTagLayout.columns;
            const r = Math.floor(pos / currentTagLayout.columns);

            const x = offXPx + c * (tagWPx + gapXPx);
            const y = offYPx + r * (tagHPx + gapYPx);

            if (bgImg) {
                ctx.drawImage(bgImg, x, y, tagWPx, tagHPx);
            }

            ctx.strokeStyle = "#cccccc";
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, tagWPx, tagHPx);

            currentTagTemplate.text_boxes.forEach((tb: any, tbIdx: number) => {
                let text = "";
                if (commonValues && tbIdx < commonValues.length && commonValues[tbIdx]) {
                    text = commonValues[tbIdx];
                } else {
                    text = entry.values[tbIdx] || "";
                }
                if (!text) return;

                const tx = x + tb.x_mm * scale;
                const ty = y + tb.y_mm * scale;
                const tw = tb.width_mm * scale;
                const th = tb.height_mm * scale;

                ctx.fillStyle = tb.color || "#000000";

                let currentFontSizePx = tb.font_size * scale / 3;
                const fontFamily = tb.font_family || 'Arial';
                const fontPrefix = `${tb.bold ? 'bold ' : ''}${tb.italic ? 'italic ' : ''}`;
                const lineSpacing = tb.line_spacing || 1.2;
                const lines = text.split('\n');

                // --- Auto-scaling logic ---
                while (currentFontSizePx > 4) {
                    ctx.font = `${fontPrefix}${currentFontSizePx}px "${fontFamily}"`;
                    let maxW = 0;
                    lines.forEach((line: string) => {
                        const w = ctx.measureText(line).width;
                        if (w > maxW) maxW = w;
                    });

                    const totalH = lines.length * currentFontSizePx * lineSpacing;

                    if (maxW <= tw && totalH <= th) {
                        break;
                    }
                    currentFontSizePx -= 0.5;
                }

                // Final application
                ctx.font = `${fontPrefix}${currentFontSizePx}px "${fontFamily}"`;

                ctx.textAlign = (tb.alignment || "center") as CanvasTextAlign;
                ctx.textBaseline = "middle";

                let textX = tx;
                if (tb.alignment === "center") textX += tw / 2;
                else if (tb.alignment === "right") textX += tw;

                const lineH = currentFontSizePx * lineSpacing;

                lines.forEach((line: string, lineIdx: number) => {
                    const lineY = ty + th / 2 + (lineIdx - (lines.length - 1) / 2) * lineH;
                    ctx.fillText(line, textX, lineY);
                });
            });
        }
    };

    if (currentTagTemplate.background_image) {
        const bgImg = new Image();
        bgImg.src = `/local-file${currentTagTemplate.background_image}`;
        bgImg.onload = () => drawContent(bgImg);
        bgImg.onerror = () => drawContent(null);
    } else {
        drawContent(null);
    }
}

document.addEventListener('DOMContentLoaded', initApp);
