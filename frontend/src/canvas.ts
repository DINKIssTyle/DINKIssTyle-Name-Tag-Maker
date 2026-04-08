// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

export class PreviewRenderer {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private tagLayout: any;
    private tagTemplate: any;
    private bgImage: HTMLImageElement | null = null;
    private currentBgPath: string = "";
    private scale: number = 1.0; // Zoom multiplier (1.0 = 100%)
    private isFit: boolean = true;

    // Drag and Drop state
    private isDragging: boolean = false;
    private isResizing: boolean = false;
    private resizeDir: string = "";
    private draggedTBIndex: number = -1;
    private dragOffsetX: number = 0;
    private dragOffsetY: number = 0;

    // Original state before resizing
    private resizeStartBox: any = null;
    private resizeStartX: number = 0;
    private resizeStartY: number = 0;

    private mmToPx: number = 0;

    constructor(canvasId: string) {
        this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        this.ctx = this.canvas.getContext('2d')!;
        this.setupInteractions();
    }

    private setupInteractions() {
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.onMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.onMouseUp());
    }

    private onMouseDown(e: MouseEvent) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) / (rect.width / this.canvas.width);
        const mouseY = (e.clientY - rect.top) / (rect.height / this.canvas.height);

        // Map mouse position to the first tag (for simplicity in property editing)
        // In this app, we edit the template, so dragging any box in any tag updates the template.
        const tagWPx = this.tagLayout.tag_width_mm * this.mmToPx;
        const tagHPx = this.tagLayout.tag_height_mm * this.mmToPx;

        const tx = 0;
        const ty = 0;

        // Check if mouse is inside this tag
        if (mouseX >= tx && mouseX <= tx + tagWPx && mouseY >= ty && mouseY <= ty + tagHPx) {
            const localX = (mouseX - tx) / this.mmToPx;
            const localY = (mouseY - ty) / this.mmToPx;

            // Hit test handles first if a text box is selected
            if (this.draggedTBIndex >= 0) {
                const handleDir = this.hitTestHandles(mouseX, mouseY, tx, ty);
                if (handleDir) {
                    this.isResizing = true;
                    this.resizeDir = handleDir;
                    const tb = this.tagTemplate.text_boxes[this.draggedTBIndex];
                    this.resizeStartBox = {
                        x: tb.x_mm, y: tb.y_mm, w: tb.width_mm, h: tb.height_mm
                    };
                    // Store initial mouse position in mm from tag origin
                    this.resizeStartX = (mouseX - tx) / this.mmToPx;
                    this.resizeStartY = (mouseY - ty) / this.mmToPx;
                    return;
                }
            }

            // Hit test background to find text boxes (reverse order for hit test)
            for (let i = this.tagTemplate.text_boxes.length - 1; i >= 0; i--) {
                const tb = this.tagTemplate.text_boxes[i];
                if (localX >= tb.x_mm && localX <= tb.x_mm + tb.width_mm &&
                    localY >= tb.y_mm && localY <= tb.y_mm + tb.height_mm) {

                    this.isDragging = true;
                    this.draggedTBIndex = i;
                    this.dragOffsetX = localX - tb.x_mm;
                    this.dragOffsetY = localY - tb.y_mm;

                    // Notify main.ts to select this TB
                    const event = new CustomEvent('tb-selected', { detail: { index: i } });
                    window.dispatchEvent(event);
                    this.draw();
                    return;
                }
            }

            // Clicked on empty area — deselect
            this.draggedTBIndex = -1;
            window.dispatchEvent(new CustomEvent('tb-deselected'));
            this.draw();
        }
    }

    private hitTestHandles(mouseX: number, mouseY: number, tx: number, ty: number): string | null {
        const tb = this.tagTemplate.text_boxes[this.draggedTBIndex];
        const tbX = tx + tb.x_mm * this.mmToPx;
        const tbY = ty + tb.y_mm * this.mmToPx;
        const tbW = tb.width_mm * this.mmToPx;
        const tbH = tb.height_mm * this.mmToPx;
        const hs = 8; // handle size in px

        const handles = [
            { dir: 'nw', x: tbX, y: tbY },
            { dir: 'n', x: tbX + tbW / 2, y: tbY },
            { dir: 'ne', x: tbX + tbW, y: tbY },
            { dir: 'w', x: tbX, y: tbY + tbH / 2 },
            { dir: 'e', x: tbX + tbW, y: tbY + tbH / 2 },
            { dir: 'sw', x: tbX, y: tbY + tbH },
            { dir: 's', x: tbX + tbW / 2, y: tbY + tbH },
            { dir: 'se', x: tbX + tbW, y: tbY + tbH },
        ];

        for (const h of handles) {
            if (mouseX >= h.x - hs / 2 && mouseX <= h.x + hs / 2 &&
                mouseY >= h.y - hs / 2 && mouseY <= h.y + hs / 2) {
                return h.dir;
            }
        }
        return null;
    }

    private onMouseMove(e: MouseEvent) {
        if (this.draggedTBIndex < 0) return;
        if (!this.isDragging && !this.isResizing) {
            // Update cursor based on hover
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left) / (rect.width / this.canvas.width);
            const mouseY = (e.clientY - rect.top) / (rect.height / this.canvas.height);
            const handleDir = this.hitTestHandles(mouseX, mouseY, 0, 0);
            if (handleDir) {
                if (handleDir === 'nw' || handleDir === 'se') this.canvas.style.cursor = 'nwse-resize';
                else if (handleDir === 'ne' || handleDir === 'sw') this.canvas.style.cursor = 'nesw-resize';
                else if (handleDir === 'n' || handleDir === 's') this.canvas.style.cursor = 'ns-resize';
                else if (handleDir === 'e' || handleDir === 'w') this.canvas.style.cursor = 'ew-resize';
            } else {
                this.canvas.style.cursor = 'default'; // Or check if over a box and show 'move'
            }
            return;
        }

        const rect = this.canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) / (rect.width / this.canvas.width);
        const mouseY = (e.clientY - rect.top) / (rect.height / this.canvas.height);

        // Again, assume we are adjusting the template relative to a tag
        // For simplicity, we use the first tag's origin to calculate movement
        const tagWPx = this.tagLayout.tag_width_mm * this.mmToPx;
        const tagHPx = this.tagLayout.tag_height_mm * this.mmToPx;

        const tb = this.tagTemplate.text_boxes[this.draggedTBIndex];

        const tx = 0;
        const ty = 0;

        if (mouseX >= tx && mouseX <= tx + tagWPx && mouseY >= ty && mouseY <= ty + tagHPx) {
            const localX = (mouseX - tx) / this.mmToPx;
            const localY = (mouseY - ty) / this.mmToPx;

            if (this.isResizing) {
                const dx = localX - this.resizeStartX;
                const dy = localY - this.resizeStartY;
                const sb = this.resizeStartBox;

                let newX = sb.x;
                let newY = sb.y;
                let newW = sb.w;
                let newH = sb.h;

                if (this.resizeDir.includes('e')) newW = sb.w + dx;
                if (this.resizeDir.includes('s')) newH = sb.h + dy;
                if (this.resizeDir.includes('w')) {
                    newX = sb.x + dx;
                    newW = sb.w - dx;
                }
                if (this.resizeDir.includes('n')) {
                    newY = sb.y + dy;
                    newH = sb.h - dy;
                }

                // Enforce minimum size and constraints
                const minS = 1.0; // 1mm minimum
                if (newW < minS) { newX -= (minS - newW) * (this.resizeDir.includes('w') ? 1 : 0); newW = minS; }
                if (newH < minS) { newY -= (minS - newH) * (this.resizeDir.includes('n') ? 1 : 0); newH = minS; }

                tb.x_mm = newX;
                tb.y_mm = newY;
                tb.width_mm = newW;
                tb.height_mm = newH;

            } else if (this.isDragging) {
                let new_x_mm = localX - this.dragOffsetX;
                let new_y_mm = localY - this.dragOffsetY;

                if (new_x_mm < 0) new_x_mm = 0;
                if (new_y_mm < 0) new_y_mm = 0;

                const SNAP_THRESHOLD_MM = 2.0;
                const centerX = (this.tagLayout.tag_width_mm - tb.width_mm) / 2;

                if (Math.abs(new_x_mm - centerX) < SNAP_THRESHOLD_MM) {
                    new_x_mm = centerX;
                } else {
                    const gridX = Math.round(new_x_mm);
                    if (Math.abs(new_x_mm - gridX) < SNAP_THRESHOLD_MM * 0.5) new_x_mm = gridX;
                }

                const gridY = Math.round(new_y_mm);
                if (Math.abs(new_y_mm - gridY) < SNAP_THRESHOLD_MM * 0.5) new_y_mm = gridY;

                tb.x_mm = new_x_mm;
                tb.y_mm = new_y_mm;
            }

            // Trigger UI update
            const event = new CustomEvent('tb-moved', {
                detail: {
                    index: this.draggedTBIndex,
                    x: tb.x_mm, y: tb.y_mm, w: tb.width_mm, h: tb.height_mm
                }
            });
            window.dispatchEvent(event);
            this.draw();
            return;
        }
    }

    private onMouseUp() {
        this.isDragging = false;
        this.isResizing = false;
        // The dragging state continues to allow editing until empty space is clicked
    }

    updateData(_paperSize: any, tagLayout: any, tagTemplate: any) {
        this.tagLayout = tagLayout;
        this.tagTemplate = tagTemplate;

        if (tagTemplate.background_image && tagTemplate.background_image !== this.currentBgPath) {
            this.currentBgPath = tagTemplate.background_image;
            this.bgImage = new Image();
            this.bgImage.src = `/local-file${tagTemplate.background_image}`;
            this.bgImage.onload = () => this.draw();
        } else if (!tagTemplate.background_image) {
            this.bgImage = null;
            this.currentBgPath = "";
        }
        this.draw();
    }

    setZoom(mode: 'fit' | 'in' | 'out' | '100') {
        if (mode === 'fit') {
            this.isFit = true;
        } else {
            this.isFit = false;
            if (mode === '100') {
                this.scale = 1.0;
            } else if (mode === 'in') {
                this.scale = Math.min(5.0, this.scale + 0.1);
            } else if (mode === 'out') {
                this.scale = Math.max(0.1, this.scale - 0.1);
            }
        }
        this.draw();
    }

    getScalePercentage(): number {
        return Math.round(this.scale * 100);
    }

    draw() {
        if (!this.ctx || !this.tagLayout || !this.tagTemplate) return;

        if (this.isFit) {
            const parent = this.canvas.parentElement;
            if (parent) {
                // padding 20px on all sides = 40px reduction
                const availW = parent.clientWidth - 40;
                const availH = parent.clientHeight - 40;
                // Tag sizes in px at 100% (1mm = 3.78px)
                const baseW = this.tagLayout.tag_width_mm * 3.78;
                const baseH = this.tagLayout.tag_height_mm * 3.78;

                const scaleX = availW / baseW;
                const scaleY = availH / baseH;
                this.scale = Math.min(scaleX, scaleY);
                if (this.scale <= 0) this.scale = 1.0;
            }
        }

        // Base 1mm = 3.78px (96dpi). Then apply user zoom scale.
        const mmToPx = 3.78 * this.scale;
        this.mmToPx = mmToPx;

        const tagWPx = this.tagLayout.tag_width_mm * mmToPx;
        const tagHPx = this.tagLayout.tag_height_mm * mmToPx;

        // Resize canvas to exactly fit the tag layout
        this.canvas.width = tagWPx;
        this.canvas.height = tagHPx;

        // Clear canvas
        this.ctx.fillStyle = "#ffffff";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Single tag rendering origin is (0,0) since canvas is exactly tag size
        const x = 0;
        const y = 0;

        // Background Image
        if (this.bgImage) {
            this.ctx.drawImage(this.bgImage, x, y, tagWPx, tagHPx);
        }

        // Draw Tag Outline
        this.ctx.strokeStyle = "#cccccc";
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y, tagWPx, tagHPx);

        // Draw Text Boxes (Placeholder rendering)
        this.tagTemplate.text_boxes.forEach((tb: any, tbIdx: number) => {
            const text = tb.label || "";
            if (!text) return;

            const tx = x + tb.x_mm * this.mmToPx;
            const ty = y + tb.y_mm * this.mmToPx;
            const tw = tb.width_mm * this.mmToPx;
            const th = tb.height_mm * this.mmToPx;

            // Draw the text box border (for visual debugging/selection)
            this.ctx.strokeStyle = (this.draggedTBIndex === tbIdx) ? "#f00" : "#add8e6";
            this.ctx.lineWidth = (this.draggedTBIndex === tbIdx) ? 2 : 1;
            this.ctx.strokeRect(tx, ty, tw, th);
            this.ctx.fillStyle = tb.color || "#000000";

            // --- Auto-scaling logic ---
            let currentFontSizePx = tb.font_size * this.mmToPx / 4; // Initial font size based on mmToPx
            const lines = text.split('\n');
            const fontFamily = tb.font_family || 'Arial';
            const fontPrefix = `${tb.bold ? 'bold ' : ''}${tb.italic ? 'italic ' : ''}`;
            const lineSpacing = tb.line_spacing || 1.2;

            while (currentFontSizePx > 4) { // Minimum font size to prevent infinite loop or too small text
                this.ctx.font = `${fontPrefix}${currentFontSizePx}px "${fontFamily}"`;

                let maxW = 0;
                lines.forEach((line: string) => {
                    const w = this.ctx.measureText(line).width;
                    if (w > maxW) maxW = w;
                });

                const totalH = lines.length * currentFontSizePx * lineSpacing;

                if (maxW <= tw && totalH <= th) {
                    break;
                }
                currentFontSizePx -= 0.5; // Decrease font size by a small increment
            }

            // Final render phase
            this.ctx.font = `${fontPrefix}${currentFontSizePx}px "${fontFamily}"`;
            this.ctx.textAlign = (tb.alignment || "center") as CanvasTextAlign;
            this.ctx.textBaseline = "middle";

            let textX = tx;
            if (tb.alignment === "center") textX += tw / 2;
            else if (tb.alignment === "right") textX += tw;

            const lineH = currentFontSizePx * lineSpacing;

            lines.forEach((line: string, lineIdx: number) => {
                const lineY = ty + th / 2 + (lineIdx - (lines.length - 1) / 2) * lineH;
                this.ctx.fillText(line, textX, lineY);
            });

            // Draw Resize Handles if selected
            if (this.draggedTBIndex === tbIdx) {
                this.ctx.fillStyle = "#ffffff";
                this.ctx.strokeStyle = "#ff0000";
                this.ctx.lineWidth = 1;
                const hs = 8; // handle size in px
                const hx = hs / 2;

                const handles = [
                    { x: tx, y: ty },
                    { x: tx + tw / 2, y: ty },
                    { x: tx + tw, y: ty },
                    { x: tx, y: ty + th / 2 },
                    { x: tx + tw, y: ty + th / 2 },
                    { x: tx, y: ty + th },
                    { x: tx + tw / 2, y: ty + th },
                    { x: tx + tw, y: ty + th },
                ];

                handles.forEach(h => {
                    this.ctx.fillRect(h.x - hx, h.y - hx, hs, hs);
                    this.ctx.strokeRect(h.x - hx, h.y - hx, hs, hs);
                });
            }
        });
    }
}
