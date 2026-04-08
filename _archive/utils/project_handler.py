# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

"""프로젝트 저장 및 불러오기 기능"""

import json
from dataclasses import asdict
from typing import Dict, Any, Tuple
import copy

from models.paper import PaperSize, TagLayout
from models.tag_data import TagTemplate, TextBox, TagEntry


def save_project(file_path: str, paper: PaperSize, layout: TagLayout, 
                 template: TagTemplate, entries: list[TagEntry], common_values: list[str]):
    """프로젝트 데이터를 JSON으로 저장"""
    
    data = {
        "version": 1,
        "paper": asdict(paper),
        "layout": asdict(layout),
        "template": {
            "background_image": template.background_image,
            "text_boxes": [asdict(tb) for tb in template.text_boxes]
        },
        "entries": [asdict(e) for e in entries],
        "common_values": common_values
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_project(file_path: str) -> dict:
    """JSON에서 프로젝트 데이터 불러오기"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    paper = PaperSize(**data.get("paper", {}))
    layout = TagLayout(**data.get("layout", {}))
    
    template_data = data.get("template", {})
    template = TagTemplate(background_image=template_data.get("background_image"))
    for tb_data in template_data.get("text_boxes", []):
        template.text_boxes.append(TextBox(**tb_data))
        
    entries = []
    for e_data in data.get("entries", []):
        entries.append(TagEntry(**e_data))
        
    common_values = data.get("common_values", [])
    
    return {
        "paper": paper,
        "layout": layout,
        "template": template,
        "entries": entries,
        "common_values": common_values
    }
