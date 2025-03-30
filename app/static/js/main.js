// IPO銘柄選定システム カスタムJavaScript

// ページ読み込み完了時の処理
document.addEventListener('DOMContentLoaded', function() {
    // フラッシュメッセージの自動消去
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // 5秒後に自動消去
    });

    // フォームバリデーション
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // ツールチップの初期化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // データ取得中のローディング表示
    const dataFetchForm = document.querySelector('form[action*="fetch-data"]');
    if (dataFetchForm) {
        dataFetchForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> データ取得中...';
                submitButton.disabled = true;
            }
            
            // ローディングオーバーレイを表示
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="spinner-container">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-white">データ取得中です。しばらくお待ちください...</p>
                </div>
            `;
            document.body.appendChild(overlay);
            
            // スタイルを追加
            const style = document.createElement('style');
            style.textContent = `
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.7);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                .spinner-container {
                    text-align: center;
                }
            `;
            document.head.appendChild(style);
        });
    }

    // フィルタリングフォームの動的な挙動
    const filterForm = document.querySelector('form[action*="filter"]');
    if (filterForm) {
        // PER入力フィールドの処理
        const perMaxInput = document.getElementById('per_max');
        if (perMaxInput) {
            perMaxInput.addEventListener('input', function() {
                validateNumericInput(this, 0, 1000);
            });
        }
        
        // 配当利回り入力フィールドの処理
        const dividendYieldInput = document.getElementById('dividend_yield_min');
        if (dividendYieldInput) {
            dividendYieldInput.addEventListener('input', function() {
                validateNumericInput(this, 0, 100);
            });
        }
        
        // 数値入力の検証
        function validateNumericInput(input, min, max) {
            let value = parseFloat(input.value);
            if (isNaN(value)) {
                input.value = '';
            } else if (value < min) {
                input.value = min;
            } else if (value > max) {
                input.value = max;
            }
        }
    }
});

// 結果テーブルの行クリック時の詳細表示
function setupResultsTable() {
    const resultsTable = document.getElementById('resultsTable');
    if (resultsTable) {
        // 直接DOMイベントを使用して行クリックを処理
        $('#resultsTable tbody').on('click', 'tr', function() {
            // クリックされた行から直接データを取得
            const cells = $(this).find('td');
            if (cells.length === 0) return;
            
            // 各セルからデータを抽出
            const stockCode = $(cells[0]).text().trim();
            const companyName = $(cells[1]).text().trim();
            const listingDate = $(cells[2]).text().trim();
            const marketSegment = $(cells[3]).text().trim();
            const currentPrice = $(cells[4]).text().trim();
            const marketCap = $(cells[5]).text().trim();
            const per = $(cells[6]).text().trim();
            const pbr = $(cells[7]).text().trim();
            const dividendYield = $(cells[8]).text().trim();
            
            // 成長フラグはバッジ要素を含むため特別な処理
            let growthFlag = '非成長';
            const badgeElement = $(cells[9]).find('.badge');
            if (badgeElement.length > 0 && badgeElement.text().includes('成長中')) {
                growthFlag = '成長中';
            }
            
            // デバッグ用にコンソールに出力
            console.log(`Clicked on stock: ${stockCode} - ${companyName}`);
            
            // 既存のモーダルを安全に削除
            try {
                const existingModal = document.getElementById('stockDetailModal');
                if (existingModal) {
                    // モーダルのbackdropを削除
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    
                    // モーダルインスタンスを取得して破棄
                    try {
                        const modalInstance = bootstrap.Modal.getInstance(existingModal);
                        if (modalInstance) {
                            modalInstance.dispose();
                        }
                    } catch (e) {
                        console.log('Modal instance not found, continuing...');
                    }
                    
                    // モーダル要素を削除
                    existingModal.remove();
                    
                    // bodyからモーダル関連のクラスを削除
                    document.body.classList.remove('modal-open');
                    
                    // スタイルプロパティを安全に削除
                    if (document.body.style.paddingRight) {
                        document.body.style.paddingRight = '';
                    }
                    
                    if (document.body.style.overflow) {
                        document.body.style.overflow = '';
                    }
                }
            } catch (error) {
                console.error('Error cleaning up modal:', error);
            }
            
            // モーダルHTMLを生成
            const modalHtml = `
                <div class="modal fade" id="stockDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${companyName} (${stockCode}) 詳細情報</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header bg-primary text-white">
                                                <h5 class="mb-0">基本情報</h5>
                                            </div>
                                            <div class="card-body">
                                                <table class="table table-sm">
                                                    <tr>
                                                        <th>証券コード</th>
                                                        <td>${stockCode}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>企業名</th>
                                                        <td>${companyName}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>上場日</th>
                                                        <td>${listingDate}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>市場区分</th>
                                                        <td>${marketSegment}</td>
                                                    </tr>
                                                </table>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header bg-success text-white">
                                                <h5 class="mb-0">財務指標</h5>
                                            </div>
                                            <div class="card-body">
                                                <table class="table table-sm">
                                                    <tr>
                                                        <th>現在価格</th>
                                                        <td>${currentPrice}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>時価総額</th>
                                                        <td>${marketCap}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>PER</th>
                                                        <td>${per}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>PBR</th>
                                                        <td>${pbr}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>配当利回り</th>
                                                        <td>${dividendYield}</td>
                                                    </tr>
                                                    <tr>
                                                        <th>成長フラグ</th>
                                                        <td>${growthFlag}</td>
                                                    </tr>
                                                </table>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>
                                <a href="https://irbank.net/${stockCode}/results" target="_blank" class="btn btn-success">
                                    <i class="fas fa-chart-line"></i> IRBankで確認
                                </a>
                                <a href="https://finance.yahoo.co.jp/quote/${stockCode}.T" target="_blank" class="btn btn-primary">
                                    <i class="fas fa-search"></i> Yahoo Financeで確認
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 新しいモーダルを追加
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // モーダルを表示
            const modal = new bootstrap.Modal(document.getElementById('stockDetailModal'));
            modal.show();
        });
    }
}

// 銘柄詳細モーダルを表示する関数
function showStockDetailModal(
    stockCode, companyName, listingDate, marketSegment,
    currentPrice, marketCap, per, pbr, dividendYield, growthFlag,
    modalTitle = null
) {
    // モーダルを作成して表示
    const modalHtml = `
        <div class="modal fade" id="stockDetailModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${modalTitle || `${companyName} (${stockCode}) 詳細情報`}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-primary text-white">
                                        <h5 class="mb-0">基本情報</h5>
                                    </div>
                                    <div class="card-body">
                                        <table class="table table-sm">
                                            <tr>
                                                <th>証券コード</th>
                                                <td>${stockCode}</td>
                                            </tr>
                                            <tr>
                                                <th>企業名</th>
                                                <td>${companyName}</td>
                                            </tr>
                                            <tr>
                                                <th>上場日</th>
                                                <td>${listingDate}</td>
                                            </tr>
                                            <tr>
                                                <th>市場区分</th>
                                                <td>${marketSegment}</td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-success text-white">
                                        <h5 class="mb-0">財務指標</h5>
                                    </div>
                                    <div class="card-body">
                                        <table class="table table-sm">
                                            <tr>
                                                <th>現在価格</th>
                                                <td>${currentPrice}</td>
                                            </tr>
                                            <tr>
                                                <th>時価総額</th>
                                                <td>${marketCap}</td>
                                            </tr>
                                            <tr>
                                                <th>PER</th>
                                                <td>${per}</td>
                                            </tr>
                                            <tr>
                                                <th>PBR</th>
                                                <td>${pbr}</td>
                                            </tr>
                                            <tr>
                                                <th>配当利回り</th>
                                                <td>${dividendYield}</td>
                                            </tr>
                                            <tr>
                                                <th>成長フラグ</th>
                                                <td>${growthFlag}</td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>
                        <a href="https://irbank.net/${stockCode}/results" target="_blank" class="btn btn-success">
                            <i class="fas fa-chart-line"></i> IRBankで確認
                        </a>
                        <a href="https://finance.yahoo.co.jp/quote/${stockCode}.T" target="_blank" class="btn btn-primary">
                            <i class="fas fa-search"></i> Yahoo Financeで確認
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 既存のモーダルを削除
    const existingModal = document.getElementById('stockDetailModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 新しいモーダルを追加
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // モーダルを表示
    const modal = new bootstrap.Modal(document.getElementById('stockDetailModal'));
    modal.show();
}

// ページ読み込み完了後に結果テーブルの設定を行う
window.addEventListener('load', function() {
    setupResultsTable();
});