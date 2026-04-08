export namespace models {
	
	export class CSVResult {
	    headers: string[];
	    data: string[][];
	
	    static createFrom(source: any = {}) {
	        return new CSVResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.headers = source["headers"];
	        this.data = source["data"];
	    }
	}
	export class PaperSize {
	    name: string;
	    width_mm: number;
	    height_mm: number;
	
	    static createFrom(source: any = {}) {
	        return new PaperSize(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.width_mm = source["width_mm"];
	        this.height_mm = source["height_mm"];
	    }
	}
	export class TagEntry {
	    checked: boolean;
	    values: string[];
	
	    static createFrom(source: any = {}) {
	        return new TagEntry(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.checked = source["checked"];
	        this.values = source["values"];
	    }
	}
	export class TextBox {
	    label: string;
	    x_mm: number;
	    y_mm: number;
	    width_mm: number;
	    height_mm: number;
	    font_family: string;
	    font_size: number;
	    line_spacing: number;
	    letter_spacing: number;
	    alignment: string;
	    color: string;
	    bold: boolean;
	    italic: boolean;
	
	    static createFrom(source: any = {}) {
	        return new TextBox(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.label = source["label"];
	        this.x_mm = source["x_mm"];
	        this.y_mm = source["y_mm"];
	        this.width_mm = source["width_mm"];
	        this.height_mm = source["height_mm"];
	        this.font_family = source["font_family"];
	        this.font_size = source["font_size"];
	        this.line_spacing = source["line_spacing"];
	        this.letter_spacing = source["letter_spacing"];
	        this.alignment = source["alignment"];
	        this.color = source["color"];
	        this.bold = source["bold"];
	        this.italic = source["italic"];
	    }
	}
	export class TagTemplate {
	    background_image?: string;
	    text_boxes: TextBox[];
	
	    static createFrom(source: any = {}) {
	        return new TagTemplate(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.background_image = source["background_image"];
	        this.text_boxes = this.convertValues(source["text_boxes"], TextBox);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class TagLayout {
	    tag_width_mm: number;
	    tag_height_mm: number;
	    columns: number;
	    rows: number;
	    offset_x_mm: number;
	    offset_y_mm: number;
	    gap_x_mm: number;
	    gap_y_mm: number;
	
	    static createFrom(source: any = {}) {
	        return new TagLayout(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.tag_width_mm = source["tag_width_mm"];
	        this.tag_height_mm = source["tag_height_mm"];
	        this.columns = source["columns"];
	        this.rows = source["rows"];
	        this.offset_x_mm = source["offset_x_mm"];
	        this.offset_y_mm = source["offset_y_mm"];
	        this.gap_x_mm = source["gap_x_mm"];
	        this.gap_y_mm = source["gap_y_mm"];
	    }
	}
	export class ProjectData {
	    version: number;
	    paper: PaperSize;
	    layout: TagLayout;
	    template: TagTemplate;
	    entries: TagEntry[];
	    common_values: string[];
	
	    static createFrom(source: any = {}) {
	        return new ProjectData(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.version = source["version"];
	        this.paper = this.convertValues(source["paper"], PaperSize);
	        this.layout = this.convertValues(source["layout"], TagLayout);
	        this.template = this.convertValues(source["template"], TagTemplate);
	        this.entries = this.convertValues(source["entries"], TagEntry);
	        this.common_values = source["common_values"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	
	
	

}

export namespace utils {
	
	export class FontInfo {
	    Family: string;
	    Path: string;
	
	    static createFrom(source: any = {}) {
	        return new FontInfo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Family = source["Family"];
	        this.Path = source["Path"];
	    }
	}

}

