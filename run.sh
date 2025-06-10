#!/bin/bash

# LLM-X4 遊戲啟動腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數定義
print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "    LLM-X4 模擬遊戲啟動器"
    echo "=================================="
    echo -e "${NC}"
}

print_usage() {
    echo "用法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  interactive    - 啟動互動模式"
    echo "  api           - 啟動API服務器"
    echo "  test          - 運行測試套件"
    echo "  demo          - 運行LLM策略演示"
    echo "  simulate N    - 運行N次遊戲模擬"
    echo "  install       - 安裝依賴"
    echo "  help          - 顯示此幫助信息"
    echo ""
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}錯誤: 未找到python3${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Python3 已找到${NC}"
}

check_dependencies() {
    echo -e "${YELLOW}檢查依賴...${NC}"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}錯誤: 未找到requirements.txt${NC}"
        exit 1
    fi
    
    # 檢查是否已安裝依賴
    python3 -c "
import sys
try:
    import numpy, yaml
    print('✓ 核心依賴已安裝')
except ImportError as e:
    print(f'⚠ 缺少依賴: {e}')
    sys.exit(1)
" || {
        echo -e "${YELLOW}正在安裝依賴...${NC}"
        python3 -m pip install -r requirements.txt
    }
}

install_dependencies() {
    echo -e "${YELLOW}安裝依賴包...${NC}"
    python3 -m pip install -r requirements.txt
    
    # 安裝可選依賴
    echo -e "${YELLOW}安裝可選依賴...${NC}"
    python3 -m pip install flask matplotlib || {
        echo -e "${YELLOW}⚠ 部分可選依賴安裝失敗，某些功能可能不可用${NC}"
    }
    
    echo -e "${GREEN}✓ 依賴安裝完成${NC}"
}

run_interactive() {
    echo -e "${GREEN}啟動互動模式...${NC}"
    python3 main.py
}

run_api() {
    echo -e "${GREEN}啟動API服務器...${NC}"
    
    # 檢查Flask是否已安裝
    python3 -c "import flask" 2>/dev/null || {
        echo -e "${YELLOW}正在安裝Flask...${NC}"
        python3 -m pip install flask
    }
    
    # 設置默認參數
    HOST=${HOST:-"0.0.0.0"}
    PORT=${PORT:-5000}
    
    echo -e "${BLUE}API服務器將在 http://${HOST}:${PORT} 啟動${NC}"
    echo -e "${BLUE}API文檔: http://${HOST}:${PORT}/api/help${NC}"
    
    python3 api_server.py --host $HOST --port $PORT
}

run_tests() {
    echo -e "${GREEN}運行測試套件...${NC}"
    python3 test_game.py
}

run_demo() {
    echo -e "${GREEN}運行LLM策略演示...${NC}"
    python3 llm_example.py
}

run_simulation() {
    local num_games=${1:-3}
    echo -e "${GREEN}運行 $num_games 次遊戲模擬...${NC}"
    python3 llm_example.py simulate $num_games
}

main() {
    print_header
    
    # 檢查Python環境
    check_python
    
    case "${1:-help}" in
        "interactive")
            check_dependencies
            run_interactive
            ;;
        "api")
            check_dependencies
            run_api
            ;;
        "test")
            check_dependencies
            run_tests
            ;;
        "demo")
            check_dependencies
            run_demo
            ;;
        "simulate")
            check_dependencies
            run_simulation $2
            ;;
        "install")
            install_dependencies
            ;;
        "help"|*)
            print_usage
            ;;
    esac
}

# 執行主函數
main "$@"
