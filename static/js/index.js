        const socket = io();

        // DOM元素
        const initialInput = document.getElementById('initialInput');
        const pageBody = document.body;
        const promptInput = document.getElementById('promptInput');
        const submitBtn = document.getElementById('submitBtn');
        const topBar = document.getElementById('topBar');
        const topBarExpanded = document.getElementById('topBarExpanded');
        const expandBtn = document.getElementById('expandBtn');
        const taskPrompt = document.getElementById('taskPrompt');
        const taskProgress = document.getElementById('taskProgress');
        const mainViewer = document.getElementById('mainViewer');
        const imageContainer = document.getElementById('imageContainer');
        const currentImage = document.getElementById('currentImage');
        const deleteBtn = document.getElementById('deleteBtn');
        const waitingState = document.getElementById('waitingState');
        const imageCounter = document.getElementById('imageCounter');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const swipeHint = document.getElementById('swipeHint');
        const noMoreHint = document.getElementById('noMoreHint');
        const loadingMore = document.getElementById('loadingMore');
        const stopBtn = document.getElementById('stopBtn');
        const continueBtn = document.getElementById('continueBtn');
        const editBtn = document.getElementById('editBtn');
        const historyBtn = document.getElementById('historyBtn');
        const historyPanel = document.getElementById('historyPanel');
        const historyClose = document.getElementById('historyClose');
        const historyList = document.getElementById('historyList');
        const logContainer = document.getElementById('logContainer');
        const logContent = document.getElementById('logContent');
        const waitingText = document.getElementById('waitingText');
        const imageGallery = document.getElementById('imageGallery');
        const galleryToggle = document.getElementById('galleryToggle');
        const galleryScroll = document.getElementById('galleryScroll');
        const sizeSelect = document.getElementById('sizeSelect');
        const screenSizeDisplay = document.getElementById('screenSizeDisplay');
        const customSizeInputs = document.getElementById('customSizeInputs');
        const customWidth = document.getElementById('customWidth');
        const customHeight = document.getElementById('customHeight');
        const initialHistoryBtn = document.getElementById('initialHistoryBtn');

        // 图片上传相关DOM元素
        const uploadArea = document.getElementById('uploadArea');
        const imageUpload = document.getElementById('imageUpload');
        const uploadPlaceholder = document.getElementById('uploadPlaceholder');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const removeImage = document.getElementById('removeImage');

        // 获取屏幕尺寸
        const screenWidth = window.screen.width;
        const screenHeight = window.screen.height;

        // 状态变量
        let images = [];
        let currentIndex = 0;
        let currentPrompt = '';
        let selectedWidth = screenWidth;  // 默认使用屏幕宽度
        let selectedHeight = screenHeight; // 默认使用屏幕高度
        let isGenerating = false;
        let autoTriggerEnabled = true;
        let statusPollingInterval = null;
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        let lastSwipeDirection = ''; // 'up' or 'down'
        let swipeHintDismissed = false; // 用户是否已关闭下滑提示
        let isTopBarExpanded = false; // 顶部栏展开状态
        let currentPromptId = null; // 当前提示词ID
        let historyRecords = []; // 历史记录列表
        let uploadedImagePath = null; // 上传的图片路径

        // 初始化显示屏幕尺寸
        function updateScreenSizeDisplay() {
            if (sizeSelect.value === 'screen') {
                screenSizeDisplay.textContent = `当前屏幕尺寸: ${screenWidth}×${screenHeight}`;
                screenSizeDisplay.style.display = 'block';
            } else {
                screenSizeDisplay.style.display = 'none';
            }
        }

        // 页面加载时显示屏幕尺寸
        updateScreenSizeDisplay();

        // 尺寸选择器事件处理
        sizeSelect.addEventListener('change', () => {
            const value = sizeSelect.value;

            if (value === 'screen') {
                // 使用屏幕尺寸
                selectedWidth = screenWidth;
                selectedHeight = screenHeight;
                customSizeInputs.classList.remove('show');
                updateScreenSizeDisplay();
            } else if (value === 'custom') {
                // 显示自定义输入框
                customSizeInputs.classList.add('show');
                screenSizeDisplay.style.display = 'none';
                // 设置默认自定义值
                if (!customWidth.value) customWidth.value = selectedWidth;
                if (!customHeight.value) customHeight.value = selectedHeight;
                selectedWidth = parseInt(customWidth.value) || 800;
                selectedHeight = parseInt(customHeight.value) || 1200;
            } else {
                // 使用预设尺寸
                const [width, height] = value.split('x').map(Number);
                selectedWidth = width;
                selectedHeight = height;
                customSizeInputs.classList.remove('show');
                screenSizeDisplay.style.display = 'none';
            }
        });

        // 自定义尺寸输入更新
        customWidth.addEventListener('input', () => {
            if (sizeSelect.value === 'custom') {
                selectedWidth = parseInt(customWidth.value) || 800;
            }
        });

        customHeight.addEventListener('input', () => {
            if (sizeSelect.value === 'custom') {
                selectedHeight = parseInt(customHeight.value) || 1200;
            }
        });

        // 图片上传处理
        uploadArea.addEventListener('click', () => {
            imageUpload.click();
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });

        // 文件选择
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });

        // 处理文件上传
        async function handleFileUpload(file) {
            if (!file.type.startsWith('image/')) {
                alert('请选择图片文件');
                return;
            }

            // 显示预览
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                uploadPlaceholder.style.display = 'none';
                imagePreview.style.display = 'flex';
            };
            reader.readAsDataURL(file);

            // 上传文件到服务器
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    uploadedImagePath = data.filepath;
                    console.log('文件上传成功:', uploadedImagePath);
                } else {
                    alert('文件上传失败: ' + data.message);
                    resetUpload();
                }
            } catch (error) {
                console.error('上传失败:', error);
                alert('文件上传失败，请重试');
                resetUpload();
            }
        }

        // 移除上传的图片
        removeImage.addEventListener('click', (e) => {
            e.stopPropagation();
            resetUpload();
        });

        // 重置上传
        function resetUpload() {
            uploadedImagePath = null;
            previewImg.src = '';
            uploadPlaceholder.style.display = 'flex';
            imagePreview.style.display = 'none';
            imageUpload.value = '';
        }

        // 刷新提示词按钮
        const refreshPromptBtn = document.getElementById('refreshPromptBtn');
        refreshPromptBtn.addEventListener('click', async () => {
            try {
                // 获取当前输入框内容
                const currentText = promptInput.value.trim();

                // 调用API获取新的提示词
                const response = await fetch('/api/prompts');
                const data = await response.json();

                if (data.success) {
                    const newPrompt = data.prompt;

                    // 如果输入框有内容，显示确认对话框（移动端简化文本）
                    if (currentText) {
                        // 检测是否为移动设备
                        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 600;

                        let confirmed;
                        if (isMobile) {
                            // 移动端使用简化提示
                            confirmed = confirm('确认替换当前内容？');
                        } else {
                            // PC端显示详细信息
                            confirmed = confirm(`即将替换当前内容：\n"${currentText}"\n\n替换为：\n"${newPrompt}"\n\n确认替换？`);
                        }

                        if (confirmed) {
                            promptInput.value = newPrompt;
                            // 添加动画效果
                            promptInput.style.animation = 'fadeIn 0.5s ease';
                            setTimeout(() => {
                                promptInput.style.animation = '';
                            }, 500);
                        }
                    } else {
                        // 直接替换
                        promptInput.value = newPrompt;
                        // 添加动画效果
                        promptInput.style.animation = 'fadeIn 0.5s ease';
                        setTimeout(() => {
                            promptInput.style.animation = '';
                        }, 500);
                    }
                } else {
                    console.error('获取提示词失败:', data.message);
                }
            } catch (error) {
                console.error('获取提示词失败:', error);
                alert('获取提示词失败，请检查配置');
            }
        });

        // 展开/收起顶部栏
        expandBtn.addEventListener('click', () => {
            isTopBarExpanded = !isTopBarExpanded;
            if (isTopBarExpanded) {
                topBarExpanded.classList.add('show');
                expandBtn.classList.add('active');
            } else {
                topBarExpanded.classList.remove('show');
                expandBtn.classList.remove('active');
            }
        });

        // 提交按钮
        submitBtn.addEventListener('click', async () => {
            const prompt = promptInput.value.trim();
            if (!prompt) {
                alert('请输入图片描述');
                return;
            }

            // 检查是否是新提示词
            const isNewPrompt = prompt !== currentPrompt;

            // 只有新提示词才清空图片
            if (isNewPrompt) {
                images = [];
                currentIndex = 0;
                currentPrompt = prompt;
                swipeHintDismissed = false; // 重置提示状态
                autoTriggerEnabled = true; // 重置自动触发
                galleryScroll.innerHTML = ''; // 清空缩略图
                logContent.textContent = ''; // 清空日志
                logContainer.classList.remove('show'); // 隐藏日志区域
                // 新提示词时不清空上传的图片，让用户可以重复使用
            }

            // 动画隐藏初始输入界面
            initialInput.classList.add('hidden');
            pageBody.classList.add('viewer-active');

            // 显示顶部栏
            setTimeout(() => {
                topBar.classList.add('show');
                taskPrompt.textContent = prompt;
                if (isNewPrompt) {
                    taskProgress.textContent = '0/∞';
                }
            }, 300);

            // 新提示词时显示等待状态
            if (isNewPrompt) {
                currentImage.style.display = 'none';
                waitingState.style.display = 'block';
            }

            // 开始生成（无限模式，不设置count），包含尺寸和图片参数
            const requestBody = {
                prompt,
                count: 999999,
                width: selectedWidth,
                height: selectedHeight
            };

            // 如果有上传的图片，添加图片路径
            if (uploadedImagePath) {
                requestBody.image_path = uploadedImagePath;
                console.log('包含上传图片:', uploadedImagePath);
            }

            const response = await fetch('/api/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                startPolling();
            }
        });

        // 轮询状态
        async function startPolling() {
            if (statusPollingInterval) clearInterval(statusPollingInterval);
            statusPollingInterval = setInterval(pollStatus, 500);
        }

        async function pollStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();

                isGenerating = status.is_running;

                // 更新进度（无限模式）
                taskProgress.textContent = `${status.generated_count}/∞`;

                // 更新停止/继续按钮和状态指示器
                if (isGenerating) {
                    stopBtn.style.display = 'flex';
                    continueBtn.style.display = 'none';
                    statusIndicator.classList.add('show');
                    statusText.textContent = `生成中`;
                    loadingMore.classList.remove('show');
                } else {
                    stopBtn.style.display = 'none';
                    continueBtn.style.display = currentPrompt ? 'flex' : 'none';
                    statusIndicator.classList.remove('show');
                }

                // 检查新图片
                if (status.images && status.images.length > images.length) {
                    const hadNoImages = images.length === 0;
                    const newImages = status.images.slice(images.length);
                    newImages.forEach((filename, idx) => {
                        const imageIndex = images.length;
                        images.push(filename);
                        addThumbnail(filename, imageIndex);
                    });

                    // 如果之前没有图片，现在有了，显示第一张
                    if (hadNoImages && images.length > 0) {
                        showImage(0);
                    }

                    updateUI();
                }
            } catch (error) {
                console.error('轮询错误:', error);
            }
        }

        // 添加缩略图到列表
        function addThumbnail(filename, index) {
            const thumb = document.createElement('div');
            thumb.className = 'gallery-thumb';
            thumb.dataset.index = index;
            thumb.dataset.filename = filename; // 添加文件名以便删除时查找

            thumb.innerHTML = `
                <img src="/static/generated/${filename}" alt="图片 ${index + 1}">
                <div class="thumb-index">${index + 1}</div>
            `;

            thumb.addEventListener('click', () => {
                showImage(index);
            });

            galleryScroll.appendChild(thumb);
        }

        // 更新缩略图激活状态
        function updateThumbnailActive() {
            const thumbs = galleryScroll.querySelectorAll('.gallery-thumb');
            thumbs.forEach((thumb, idx) => {
                if (idx === currentIndex) {
                    thumb.classList.add('active');
                    // 滚动到当前缩略图
                    thumb.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                } else {
                    thumb.classList.remove('active');
                }
            });
        }

        // 显示图片
        function showImage(index, direction = '') {
            if (index < 0 || index >= images.length) return;

            currentIndex = index;

            // 添加切换动画
            if (direction) {
                currentImage.classList.remove('slide-up', 'slide-down');
                void currentImage.offsetWidth; // 触发重绘
                currentImage.classList.add(direction === 'up' ? 'slide-up' : 'slide-down');
            }

            currentImage.src = `/static/generated/${images[index]}?t=${Date.now()}`;
            currentImage.style.display = 'block';
            waitingState.style.display = 'none';
            deleteBtn.style.display = 'flex'; // 显示删除按钮

            updateUI();
        }

        // 更新UI状态
        function updateUI() {
            // 更新计数器
            if (images.length > 0) {
                imageCounter.textContent = `${currentIndex + 1}/${images.length}`;
            }

            // 更新缩略图激活状态
            updateThumbnailActive();

            // 显示/隐藏图片列表切换按钮
            if (images.length > 0) {
                galleryToggle.classList.add('show');
            } else {
                galleryToggle.classList.remove('show');
            }

            // 显示下滑提示（只在第一次有多张图片时显示，且用户未关闭）
            if (!swipeHintDismissed && images.length > 1 && currentIndex === 0) {
                swipeHint.classList.add('show');
                // 6秒后自动隐藏（3次bounce动画）
                setTimeout(() => {
                    swipeHint.classList.remove('show');
                }, 6000);
            } else {
                swipeHint.classList.remove('show');
            }
        }

        // 添加更多图片
        async function addMoreImages(count) {
            console.log('请求更多图片:', count);
            loadingMore.classList.add('show');

            const response = await fetch('/api/add_more', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count })
            });

            if (response.ok) {
                startPolling();
            }
        }

        // 触摸事件处理
        mainViewer.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        mainViewer.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].clientX;
            touchEndY = e.changedTouches[0].clientY;
            handleSwipe();
        });

        // 处理滑动
        function handleSwipe() {
            const deltaX = touchStartX - touchEndX;
            const deltaY = touchStartY - touchEndY;

            // 判断是水平滑动还是垂直滑动
            const isHorizontalSwipe = Math.abs(deltaX) > Math.abs(deltaY);

            if (isHorizontalSwipe) {
                // 水平滑动 - 切换图片
                if (Math.abs(deltaX) > 50) {
                    if (deltaX > 0) {
                        // 左滑 - 下一张
                        if (currentIndex < images.length - 1) {
                            showImage(currentIndex + 1, 'up');
                        } else {
                            // 已经是最后一张，显示提示
                            if (images.length > 0) {
                                if (isGenerating) {
                                    noMoreHint.textContent = '正在生成更多图片...';
                                } else {
                                    noMoreHint.textContent = '已经是最后一张了';
                                }
                                noMoreHint.classList.add('show');
                                setTimeout(() => {
                                    noMoreHint.classList.remove('show');
                                }, 2000);
                            }
                        }
                    } else {
                        // 右滑 - 上一张
                        if (currentIndex > 0) {
                            showImage(currentIndex - 1, 'down');
                        } else {
                            // 已经是第一张
                            noMoreHint.textContent = '已经是第一张了';
                            noMoreHint.classList.add('show');
                            setTimeout(() => {
                                noMoreHint.classList.remove('show');
                            }, 2000);
                        }
                    }
                }
            } else {
                // 垂直滑动
                if (Math.abs(deltaY) > 50) {
                    if (deltaY > 0) {
                        // 上滑 - 打开图片列表
                        if (images.length > 0 && !imageGallery.classList.contains('open')) {
                            imageGallery.classList.add('open');
                            galleryToggle.classList.add('active');
                        }
                    } else {
                        // 下滑 - 关闭图片列表（如果已打开）
                        if (imageGallery.classList.contains('open')) {
                            imageGallery.classList.remove('open');
                            galleryToggle.classList.remove('active');
                        }
                    }
                }
            }
        }

        // 页面加载时检查状态
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();

                console.log('加载状态:', status);

                // 判断是否有活动任务或历史数据
                const hasActiveTask = status.is_running || status.current_prompt;
                const hasImages = status.images && status.images.length > 0;

                if (hasActiveTask || hasImages) {
                    // 恢复状态
                    images = status.images || [];
                    currentPrompt = status.current_prompt || '';
                    selectedWidth = status.width || 800;
                    selectedHeight = status.height || 1200;
                    autoTriggerEnabled = !status.is_running;
                    isGenerating = status.is_running;

                    // 隐藏初始输入
                    initialInput.classList.add('hidden');
                    pageBody.classList.add('viewer-active');

                    // 显示顶部栏
                    topBar.classList.add('show');
                    taskPrompt.textContent = currentPrompt;
                    taskProgress.textContent = `${status.generated_count}/∞`;

                    // 恢复缩略图列表
                    galleryScroll.innerHTML = '';
                    images.forEach((filename, index) => {
                        addThumbnail(filename, index);
                    });

                    // 如果有图片，显示第一张
                    if (hasImages) {
                        showImage(0);
                        waitingState.style.display = 'none';
                    } else {
                        // 没有图片，显示等待状态
                        currentImage.style.display = 'none';
                        waitingState.style.display = 'block';
                    }

                    // 如果正在生成，开始轮询
                    if (status.is_running) {
                        startPolling();
                    }

                    console.log('✅ 状态已恢复 - 正在运行:', status.is_running, '图片数量:', images.length);
                } else {
                    console.log('📝 无历史数据，显示初始输入界面');
                }
            } catch (error) {
                console.error('加载状态失败:', error);
            }
        });

        // 停止按钮
        stopBtn.addEventListener('click', async () => {
            const response = await fetch('/api/stop', {
                method: 'POST'
            });

            if (response.ok) {
                isGenerating = false;
                stopBtn.style.display = 'none';
                continueBtn.style.display = 'flex';
                loadingMore.classList.remove('show');
                statusIndicator.classList.remove('show');

                if (statusPollingInterval) {
                    clearInterval(statusPollingInterval);
                    statusPollingInterval = null;
                }
            }
        });

        // 继续生成按钮
        continueBtn.addEventListener('click', async () => {
            if (!currentPrompt) return;

            const requestBody = {
                prompt: currentPrompt,
                count: 999999,
                width: selectedWidth,
                height: selectedHeight
            };

            // 如果有上传的图片，添加图片路径
            if (uploadedImagePath) {
                requestBody.image_path = uploadedImagePath;
            }

            const response = await fetch('/api/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                continueBtn.style.display = 'none';
                stopBtn.style.display = 'flex';
                startPolling();
            }
        });

        // 删除按钮
        deleteBtn.addEventListener('click', async () => {
            if (images.length === 0) return;

            const currentFilename = images[currentIndex];
            const confirmed = confirm(`确定要删除这张图片吗？\n\n图片：${currentFilename}`);

            if (!confirmed) return;

            try {
                const response = await fetch('/api/delete_image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: currentFilename })
                });

                const result = await response.json();

                if (result.success) {
                    // 更新本地图片列表
                    images = result.images;

                    // 删除缩略图
                    const thumbToRemove = document.querySelector(`.gallery-thumb[data-filename="${currentFilename}"]`);
                    if (thumbToRemove) {
                        thumbToRemove.remove();
                    }

                    // 如果还有图片，显示下一张或上一张
                    if (images.length > 0) {
                        // 调整当前索引
                        if (currentIndex >= images.length) {
                            currentIndex = images.length - 1;
                        }
                        showImage(currentIndex);
                    } else {
                        // 没有图片了，隐藏删除按钮和图片
                        currentImage.style.display = 'none';
                        deleteBtn.style.display = 'none';
                        waitingState.style.display = 'block';
                        document.getElementById('waitingText').textContent = '所有图片已删除';
                    }

                    updateUI();
                } else {
                    alert('删除失败: ' + result.message);
                }
            } catch (error) {
                console.error('删除图片失败:', error);
                alert('删除失败，请重试');
            }
        });

        // 历史记录按钮（顶部栏）
        historyBtn.addEventListener('click', async () => {
            historyPanel.classList.add('show');
            await loadHistory();
        });

        // 历史记录按钮（首页）
        if (initialHistoryBtn) {
            initialHistoryBtn.addEventListener('click', async () => {
                historyPanel.classList.add('show');
                await loadHistory();
            });
        } else {
            console.error('未找到 initialHistoryBtn 元素');
        }

        // 关闭历史记录面板
        historyClose.addEventListener('click', () => {
            historyPanel.classList.remove('show');
        });

        // 加载历史记录
        async function loadHistory() {
            try {
                console.log('开始加载历史记录...');
                const response = await fetch('/api/history');
                console.log('历史记录响应状态:', response.status);
                const data = await response.json();
                console.log('历史记录数据:', data);

                if (data.success) {
                    historyRecords = data.records;
                    console.log('历史记录数量:', historyRecords.length);
                    renderHistory();
                } else {
                    console.error('获取历史记录失败:', data.message);
                    historyList.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px;">加载失败，请重试</div>';
                }
            } catch (error) {
                console.error('加载历史记录失败:', error);
                historyList.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px;">加载失败：' + error.message + '</div>';
            }
        }

        // 渲染历史记录列表
        function renderHistory() {
            console.log('renderHistory 被调用, 记录数:', historyRecords.length);

            if (historyRecords.length === 0) {
                console.log('没有历史记录');
                historyList.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px;">暂无历史记录</div>';
                return;
            }

            console.log('开始渲染历史记录...');
            const html = historyRecords.map(record => {
                const isActive = record.id === currentPromptId;
                // 限制提示词显示长度
                const displayPrompt = record.prompt.length > 100 ? record.prompt.substring(0, 100) + '...' : record.prompt;
                return `
                    <div class="history-item ${isActive ? 'active' : ''}" data-id="${record.id}">
                        <div class="history-item-prompt">${displayPrompt}</div>
                        <div class="history-item-meta">
                            <span class="history-item-count">📷 ${record.image_count || 0} 张</span>
                            <button class="history-item-delete" onclick="deleteHistoryItem('${record.id}', event)">删除</button>
                        </div>
                    </div>
                `;
            }).join('');

            console.log('生成的 HTML 长度:', html.length);
            historyList.innerHTML = html;
            console.log('HTML 已设置到 historyList');

            // 添加点击事件
            const items = document.querySelectorAll('.history-item');
            console.log('找到历史项数量:', items.length);

            items.forEach(item => {
                item.addEventListener('click', async (e) => {
                    if (e.target.classList.contains('history-item-delete')) return;

                    const promptId = item.dataset.id;
                    console.log('点击历史项:', promptId);
                    await switchToHistory(promptId);
                });
            });

            console.log('历史记录渲染完成');
        }

        // 切换到历史提示词
        async function switchToHistory(promptId) {
            try {
                const response = await fetch('/api/switch_prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt_id: promptId })
                });

                const data = await response.json();

                if (data.success) {
                    currentPromptId = promptId;
                    currentPrompt = data.record.prompt;
                    images = data.images || [];
                    currentIndex = 0;

                    // 同步尺寸参数
                    selectedWidth = data.record.width || 800;
                    selectedHeight = data.record.height || 1200;

                    // 关闭历史面板
                    historyPanel.classList.remove('show');

                    // 清空缩略图并重新添加
                    galleryScroll.innerHTML = '';
                    images.forEach((img, idx) => {
                        addThumbnail(img, idx);
                    });

                    // 显示第一张图片
                    if (images.length > 0) {
                        showImage(0);
                        topBar.classList.add('show');
                        initialInput.classList.add('hidden');
                        pageBody.classList.add('viewer-active');
                        taskPrompt.textContent = currentPrompt;
                        taskProgress.textContent = `${images.length}/∞`;
                    } else {
                        // 没有图片，也要显示顶部栏
                        topBar.classList.add('show');
                        initialInput.classList.add('hidden');
                        pageBody.classList.add('viewer-active');
                        taskPrompt.textContent = currentPrompt;
                        taskProgress.textContent = `0/∞`;
                    }

                    // 更新按钮状态 - 显示继续按钮
                    stopBtn.style.display = 'none';
                    continueBtn.style.display = 'flex';
                    statusIndicator.classList.remove('show');

                    updateUI();
                }
            } catch (error) {
                console.error('切换历史记录失败:', error);
                alert('切换失败，请重试');
            }
        }

        // 删除历史记录项
        window.deleteHistoryItem = async function(promptId, event) {
            event.stopPropagation();

            const confirmed = confirm('确定要删除这条历史记录及所有相关图片吗？');
            if (!confirmed) return;

            try {
                const response = await fetch(`/api/history/${promptId}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    // 如果删除的是当前提示词，清空状态
                    if (promptId === currentPromptId) {
                        images = [];
                        currentPrompt = '';
                        currentPromptId = null;
                        currentIndex = 0;
                        galleryScroll.innerHTML = '';
                        currentImage.style.display = 'none';
                        deleteBtn.style.display = 'none';
                        waitingState.style.display = 'block';
                        initialInput.classList.remove('hidden');
                        pageBody.classList.remove('viewer-active');
                        topBar.classList.remove('show');
                    }

                    // 重新加载历史记录
                    await loadHistory();
                }
            } catch (error) {
                console.error('删除历史记录失败:', error);
                alert('删除失败，请重试');
            }
        };

        // 修改提示词按钮
        editBtn.addEventListener('click', () => {
            // 确认是否要修改（会清空当前图片）
            if (images.length > 0) {
                if (!confirm('修改提示词将清空当前图片，是否继续？')) {
                    return;
                }
            }

            // 显示输入界面
            initialInput.classList.remove('hidden');
            pageBody.classList.remove('viewer-active');
            promptInput.value = currentPrompt;
            promptInput.focus();

            // 恢复尺寸选择器状态
            updateScreenSizeDisplay();
        });

        // 点击下滑提示关闭
        swipeHint.addEventListener('click', () => {
            swipeHintDismissed = true;
            swipeHint.classList.remove('show');
        });

        // 图片列表切换
        galleryToggle.addEventListener('click', () => {
            imageGallery.classList.toggle('open');
            galleryToggle.classList.toggle('active');
        });

        // Socket进度更新
        socket.on('progress', (data) => {
            console.log('收到进度更新:', data);

            // 根据状态更新等待文字
            if (data.status === 'generating_prompt') {
                waitingText.textContent = '正在生成提示词...';
                // 生成提示词时显示日志区域
                logContainer.classList.add('show');
            } else if (data.status === 'generating_image') {
                waitingText.textContent = '正在生成图片...';
            } else {
                waitingText.textContent = '正在生成图片...';
            }
        });

        // Socket日志处理
        socket.on('log', (data) => {
            console.log('收到日志:', data.message);

            // 添加日志到显示区域
            logContent.textContent += data.message;

            // 自动滚动到底部
            logContainer.scrollTop = logContainer.scrollHeight;
        });

        // Socket错误处理
        socket.on('error', (data) => {
            console.error('错误:', data);
            alert('错误: ' + data.message);
        });

        // ========== PC 键盘支持 ==========
        // 键盘事件处理（支持上下左右键）
        document.addEventListener('keydown', (e) => {
            // 如果在输入框中，不处理键盘事件
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                return;
            }

            // 如果初始输入界面或历史面板可见，不处理图片切换
            if (!initialInput.classList.contains('hidden') || historyPanel.classList.contains('show')) {
                return;
            }

            // 如果没有图片，不处理
            if (images.length === 0) {
                return;
            }

            switch(e.key) {
                case 'ArrowUp':      // 上键 - 上一张
                case 'ArrowLeft':    // 左键 - 上一张
                    e.preventDefault();
                    if (currentIndex > 0) {
                        showImage(currentIndex - 1, 'down');
                        console.log('⬆️ 键盘：上一张', currentIndex + 1, '/', images.length);
                    } else {
                        // 已经是第一张
                        showToast('已经是第一张了');
                    }
                    break;

                case 'ArrowDown':    // 下键 - 下一张
                case 'ArrowRight':   // 右键 - 下一张
                    e.preventDefault();
                    if (currentIndex < images.length - 1) {
                        showImage(currentIndex + 1, 'up');
                        console.log('⬇️ 键盘：下一张', currentIndex + 1, '/', images.length);
                    } else {
                        // 已经是最后一张
                        if (isGenerating) {
                            showToast('正在生成更多图片...');
                        } else {
                            showToast('已经是最后一张了');
                        }
                    }
                    break;

                case 'Home':         // Home键 - 第一张
                    e.preventDefault();
                    if (currentIndex !== 0) {
                        showImage(0, 'down');
                        console.log('🏠 键盘：跳转到第一张');
                    }
                    break;

                case 'End':          // End键 - 最后一张
                    e.preventDefault();
                    if (currentIndex !== images.length - 1) {
                        showImage(images.length - 1, 'up');
                        console.log('🔚 键盘：跳转到最后一张');
                    }
                    break;

                case 'Delete':       // Delete键 - 删除当前图片
                    e.preventDefault();
                    if (images.length > 0 && deleteBtn.style.display !== 'none') {
                        deleteBtn.click();
                    }
                    break;

                case ' ':            // 空格键 - 切换底部图片列表
                    e.preventDefault();
                    galleryToggle.click();
                    break;

                case 'Escape':       // ESC键 - 关闭历史面板或底部列表
                    e.preventDefault();
                    if (historyPanel.classList.contains('show')) {
                        historyPanel.classList.remove('show');
                    } else if (imageGallery.classList.contains('open')) {
                        galleryToggle.click();
                    }
                    break;
            }
        });

        // 显示提示消息
        function showToast(message) {
            // 复用 noMoreHint 元素来显示提示
            noMoreHint.textContent = message;
            noMoreHint.classList.add('show');
            setTimeout(() => {
                noMoreHint.classList.remove('show');
            }, 1500);
        }

        console.log('✅ PC 键盘支持已启用：上下左右键切换图片，Home/End跳转，Delete删除，空格切换列表，ESC关闭面板');
    
