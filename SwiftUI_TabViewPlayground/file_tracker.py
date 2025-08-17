#!/usr/bin/env python3
"""
Git File Tracker for SwiftUI Projects
Tự động theo dõi và cập nhật các file theo loại khi có commit mới hoặc build trong Xcode.
"""

import os
import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
import argparse
import logging
import fnmatch
import sys
import math

# ===== KHAI BÁO BIẾN fileList TOÀN CỤC (để trống cho sử dụng qua command line) =====
fileList: List[str] = []
# ============================================

class GitFileTracker:
    def __init__(self, project_path: str, output_dir: str = "tracked_files"):
        self.project_path = Path(project_path).resolve()
        self.output_dir = self.project_path / output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Cấu hình cho dự án SwiftUI/Xcode
        self.file_types = {
            'swift': ['.swift'],
            'objective_c': ['.h', '.m', '.mm'],
        }

        self.ignore_patterns: Set[str] = {
            'build/', 'DerivedData/', '.swiftpm/',
            '*.xcodeproj/', '*.xcworkspace/', 'xcuserdata/',
            'Package.resolved',
            '.git/', '.vscode/', '.idea/', 'coverage/', '.cache/',
            '.DS_Store', '*.log',
        }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'tracker.log'),
                logging.StreamHandler(sys.stdout) # In log ra stdout để Xcode có thể bắt được
            ]
        )
        self.logger = logging.getLogger(__name__)

        self.metadata_file = self.output_dir / 'metadata.json'
        self.load_metadata()

    def load_metadata(self):
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                self.logger.error(f"Error decoding JSON from {self.metadata_file}. Initializing new metadata.")
                self._initialize_metadata()
        else:
            self._initialize_metadata()

    def _initialize_metadata(self):
        self.metadata = {
            'last_commit': None,
            'tracked_files': {},
            'file_hashes': {},
            'created': datetime.now().isoformat()
        }

    def save_metadata(self):
        self.metadata['updated'] = datetime.now().isoformat()
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def get_current_commit(self) -> str | None:
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_path, capture_output=True, text=True, check=True, encoding='utf-8'
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Không thể lấy commit hash hiện tại. Đảm bảo 'git' đã cài đặt và đây là một git repo. Lỗi: {e}")
            return None

    def get_tracked_files(self) -> List[str]:
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=self.project_path, capture_output=True, text=True, check=True, encoding='utf-8'
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f and not self.should_ignore_file(f)]
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Không thể lấy danh sách file tracked. Lỗi: {e}")
            return []

    def get_changed_files(self, since_commit: str | None = None) -> List[str]:
        try:
            cmd = ['git', 'diff', '--name-only', f'{since_commit}..HEAD'] if since_commit else ['git', 'diff', '--name-only', '--cached']
            result = subprocess.run(
                cmd, cwd=self.project_path, capture_output=True, text=True, check=True, encoding='utf-8'
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f and not self.should_ignore_file(f)]
        except subprocess.CalledProcessError:
            return [] # Bình thường nếu không có thay đổi
        except FileNotFoundError:
            self.logger.error("Lệnh 'git' không tìm thấy khi lấy file thay đổi.")
            return []
            
    def should_ignore_file(self, file_path: str) -> bool:
        path_obj = Path(file_path)
        normalized_path_str = str(path_obj).replace('\\', '/')
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'):
                if f"/{pattern}" in f"/{normalized_path_str}/" or normalized_path_str.startswith(pattern):
                    return True
            else:
                if fnmatch.fnmatch(path_obj.name, pattern):
                    return True
        return False

    def get_file_type(self, file_path: str) -> str:
        file_ext = Path(file_path).suffix.lower()
        for type_name, extensions in self.file_types.items():
            if file_ext in extensions:
                return type_name
        if file_ext == '.plist': return 'configuration'
        if file_ext == '.entitlements': return 'configuration'
        if file_ext in ['.storyboard', '.xib']: return 'interface_builder'
        if file_ext == '.metal': return 'metal_shader'
        if file_ext == '.json': return 'config'
        if file_ext == '.md': return 'markdown'
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.heic', '.webp', 
                        '.mp3', '.wav', '.m4a', '.aiff', '.mp4', '.mov', '.usdz', '.scn', '.dae']:
            return 'assets'
        return 'other'

    def calculate_file_hash(self, file_path: Path) -> str | None:
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (FileNotFoundError, IOError) as e:
            self.logger.warning(f"Không thể hash file {file_path}: {e}")
            return None

    def read_file_content(self, file_path: Path) -> str:
        try:
            return file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError, FileNotFoundError) as e:
            self.logger.warning(f"Không thể đọc file: {file_path} - {e}")
            return f"# FAILED_TO_READ_FILE: {file_path.name}\n"

    def create_consolidated_file(self, file_type: str, files: List[str]):
        output_file = self.output_dir / f"{file_type}_files.txt"
        content = [
            f"# Consolidated {file_type.upper()} Files",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Total files: {len(files)}",
            "=" * 80, ""
        ]
        for file_path_str in sorted(files):
            full_path = self.project_path / file_path_str
            if full_path.is_file():
                normalized_path = file_path_str.replace('\\', '/')
                content.extend([f"# FILE: {normalized_path}", "-" * 60, self.read_file_content(full_path), "", "=" * 80, ""])
        output_file.write_text('\n'.join(content), encoding='utf-8')
        self.logger.info(f"Tạo file tổng hợp: {output_file} ({len(files)} files)")

    def create_project_structure(self):
        structure_file = self.output_dir / "project_structure.txt"
        content = [f"# Project Structure - {self.project_path.name}", f"# Generated: {datetime.now().isoformat()}", "="*80, ""]
        content.extend(self.generate_tree_structure())
        content.extend(["", "="*80, "# STATISTICS", "="*80])
        content.extend(self.get_project_statistics())
        structure_file.write_text('\n'.join(content), encoding='utf-8')
        self.logger.info(f"Tạo file cấu trúc dự án: {structure_file}")

    def generate_tree_structure(self) -> List[str]:
        tree_lines = []
        # Cấu trúc cây file, ví dụ: {'src': {'main.py': {'_is_file': True, ...}}}
        file_tree = {}
        
        # Lấy danh sách file mới nhất từ git để xây dựng cây
        tracked_files_for_tree = self.get_tracked_files()

        for file_path_str in tracked_files_for_tree:
            parts = Path(file_path_str).parts
            current_level = file_tree
            for i, part in enumerate(parts):
                is_file_node = (i == len(parts) - 1)
                
                # Đây là điểm mấu chốt: nếu part chưa có trong current_level, 
                # chúng ta luôn tạo một dictionary mới cho nó.
                if part not in current_level:
                    current_level[part] = {} # LUÔN TẠO DICTIONARY
                
                # Sau đó, nếu nó là một file, chúng ta thêm các thuộc tính vào dictionary đó.
                if is_file_node:
                    current_level[part]['_is_file'] = True
                    current_level[part]['_type'] = self.get_file_type(file_path_str)

                # Di chuyển xuống cấp tiếp theo
                current_level = current_level[part]

        tree_lines.append(f"{self.project_path.name}/")
        # Bắt đầu xây dựng cây từ gốc
        self._build_tree_recursive(file_tree, tree_lines, "")
        return tree_lines

    def _build_tree_recursive(self, node: dict, lines: List[str], prefix: str):
        # Lọc ra các mục không phải là key nội bộ (bắt đầu bằng '_')
        items_to_process = [item for item in node.items() if not item[0].startswith('_')]
        
        # Sắp xếp: thư mục trước, file sau, rồi theo tên
        sorted_items = sorted(
            items_to_process, 
            key=lambda x: (x[1].get('_is_file', False), x[0].lower())
        )

        for i, (name, value) in enumerate(sorted_items):
            is_last = (i == len(sorted_items) - 1)
            connector = "└── " if is_last else "├── "
            children_prefix = prefix + ("    " if is_last else "│   ")
            
            # Bây giờ 'value' luôn là một dictionary, nên .get() sẽ luôn hoạt động
            if value.get('_is_file', False):
                # Là file
                file_type = value.get('_type', 'other')
                indicator = self._get_file_type_indicator(file_type)
                lines.append(f"{prefix}{connector}{name} {indicator}")
            else:
                # Là thư mục
                lines.append(f"{prefix}{connector}{name}/")
                self._build_tree_recursive(value, lines, children_prefix)

    def _get_file_type_indicator(self, file_type: str) -> str:
        indicators = {'swift': '🐦', 'objective_c': '🅾️', 'interface_builder': '🎨', 'configuration': '⚙️', 'metal_shader': '✨', 'markdown': '📝', 'assets': '🖼️', 'config': '🔧', 'other': '📄'}
        return indicators.get(file_type, '📄')

    def get_project_statistics(self) -> List[str]:
        tracked_files = self.get_tracked_files()
        stats = [f"Total tracked files (respecting ignores): {len(tracked_files)}"]
        files_by_type_counts: Dict[str, int] = {}
        total_size = 0
        for file_path_str in tracked_files:
            file_type = self.get_file_type(file_path_str)
            files_by_type_counts[file_type] = files_by_type_counts.get(file_type, 0) + 1
            full_path = self.project_path / file_path_str
            if full_path.is_file():
                try: total_size += full_path.stat().st_size
                except FileNotFoundError: pass
        stats.append(f"Total size: {self._format_size(total_size)}")
        stats.append("\nFiles by type:")
        if tracked_files:
            for ft, count in sorted(files_by_type_counts.items()):
                stats.append(f"  {self._get_file_type_indicator(ft)} {ft.capitalize()}: {count} files ({(count / len(tracked_files)) * 100:.1f}%)")
        return stats

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0: return "0B"
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def initial_scan(self):
        self.logger.info("Performing initial scan of the project...")
        all_tracked_files = self.get_tracked_files()
        files_by_type_map: Dict[str, List[str]] = {}
        for file_path in all_tracked_files:
            files_by_type_map.setdefault(self.get_file_type(file_path), []).append(file_path)
        
        for file_type, files in files_by_type_map.items():
            self.create_consolidated_file(file_type, files)
        
        self.create_project_structure()
        
        current_commit = self.get_current_commit()
        self.metadata['last_commit'] = current_commit
        self.metadata['tracked_files'] = files_by_type_map
        self.metadata['file_hashes'] = {
            f: self.calculate_file_hash(self.project_path / f) for f in all_tracked_files if self.calculate_file_hash(self.project_path / f)
        }
        self.save_metadata()
        self.logger.info(f"Initial scan complete. Tracked {len(all_tracked_files)} files.")

    def check_and_update(self):
        self.logger.info("Checking for updates...")
        current_commit = self.get_current_commit()
        if not current_commit:
            self.logger.error("Could not get current commit. Aborting update.")
            return

        last_commit = self.metadata.get('last_commit')
        if not last_commit:
            self.logger.info("No previous scan found. Performing initial scan instead.")
            self.initial_scan()
            return
        
        if last_commit == current_commit:
            self.logger.info(f"No new commits since {last_commit}. Checking for local file changes...")
        else:
            self.logger.info(f"New commit detected: {current_commit} (was {last_commit}).")

        all_current_files = self.get_tracked_files()
        old_hashes = self.metadata.get('file_hashes', {})
        
        changed_files = {path for path in all_current_files if self.calculate_file_hash(self.project_path / path) != old_hashes.get(path)}
        new_files = set(all_current_files) - set(old_hashes.keys())
        deleted_files = set(old_hashes.keys()) - set(all_current_files)
        
        if not any([changed_files, new_files, deleted_files]):
            self.logger.info("No changes detected. Project is up-to-date.")
            return
            
        self.logger.info(f"Found {len(new_files)} new, {len(changed_files)} changed, {len(deleted_files)} deleted files.")

        # Update metadata and consolidated files
        current_files_by_type: Dict[str, List[str]] = {}
        for f in all_current_files:
            current_files_by_type.setdefault(self.get_file_type(f), []).append(f)
        
        affected_types = {self.get_file_type(f) for f in changed_files | new_files | deleted_files}

        for file_type in affected_types:
            files_of_type = current_files_by_type.get(file_type, [])
            if files_of_type:
                self.create_consolidated_file(file_type, files_of_type)
            else:
                consolidated_file = self.output_dir / f"{file_type}_files.txt"
                if consolidated_file.exists():
                    consolidated_file.unlink()
                    self.logger.info(f"Removed empty consolidated file: {consolidated_file}")

        self.create_project_structure()

        self.metadata['last_commit'] = current_commit
        self.metadata['tracked_files'] = current_files_by_type
        self.metadata['file_hashes'] = {f: self.calculate_file_hash(self.project_path / f) for f in all_current_files if self.calculate_file_hash(self.project_path / f)}
        self.save_metadata()
        self.logger.info("Update complete.")
    
    def status(self):
        print(f"\n=== Git File Tracker Status ===")
        print(f"Project: {self.project_path}")
        print(f"Output: ./{self.output_dir.relative_to(self.project_path)}")
        last_commit = self.metadata.get('last_commit', 'None')
        current_commit = self.get_current_commit() or "N/A"
        print(f"Last Processed Commit: {last_commit}")
        print(f"Current Git HEAD:      {current_commit}")
        if last_commit != current_commit:
            print("Status: ⚠️  New commits detected. Run --check-update or build the project.")
        else:
            print("Status: ✅  Up-to-date with the latest commit.")

# (Phần còn lại của các hàm merge không thay đổi)
# ...

def main():
    parser = argparse.ArgumentParser(description='Git File Tracker for SwiftUI Projects')
    parser.add_argument('--project-path', default=os.getcwd(), help='Path to the project directory.')
    parser.add_argument('--output-dir', default='tracked_files', help='Output directory name.')
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--initial-scan', action='store_true', help='Perform a full scan of the project.')
    action_group.add_argument('--check-update', action='store_true', help='Check for changes since the last scan.')
    action_group.add_argument('--status', action='store_true', help='Show the current tracking status.')
    
    args = parser.parse_args()
    
    tracker = GitFileTracker(args.project_path, args.output_dir)
    
    if args.initial_scan:
        tracker.initial_scan()
    elif args.check_update:
        tracker.check_and_update()
    elif args.status:
        tracker.status()

if __name__ == '__main__':
    main()