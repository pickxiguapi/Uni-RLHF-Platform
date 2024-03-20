/**
 * 画布中绘制矩形
 * 参数: cav-画布对象  list-矩形数组 i-选中矩形下标
 **/
/* 操作执行方法分发 */
export function draw(cav, list, i) {
    // 画布初始化
    let ctx = cav.getContext('2d');
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 2;
 
    // 变量初始化
    let sX = 0; // 鼠标X坐标
    let sY = 0; // 鼠标Y坐标
 
    /*
     *鼠标移动进行第一层判断, 区分情况: 无矩形, 已有矩形无选中, 已有选中矩形
     */
    cav.onmousemove = function (em) {
        sX = em.offsetX;
        sY = em.offsetY;
        let iem = undefined; // 鼠标移动时临时存储当前鼠标所在矩形的下标
 
        if (list.length === 0) { // **** 无矩形 ****
            // 绘制新矩形
            newDraw(cav, ctx, list);
        } else if (i === undefined) { // **** 已有矩形无选中 ****
            // 判断鼠标位置
            list.forEach(function (value, index, array) {
                if (value.w > 0 && value.h > 0 && sX > value.x && sX < value.x + value.w && sY > value.y && sY < value.y + value.h) {
                    // 鼠标在右下方向生成的矩形中
                    iem = index;
                    judgeDraw(cav, ctx, list, iem);
                }
                if (value.w < 0 && value.h > 0 && sX < value.x && sX > value.x + value.w && sY > value.y && sY < value.y + value.h) {
                    // 鼠标在左下方向生成的矩形中
                    iem = index;
                    judgeDraw(cav, ctx, list, iem);
                }
                if (value.w > 0 && value.h < 0 && sX > value.x && sX < value.x + value.w && sY < value.y && sY > value.y + value.h) {
                    // 鼠标在右上方向生成的矩形中
                    iem = index;
                    judgeDraw(cav, ctx, list, iem);
                }
                if (value.w < 0 && value.h < 0 && sX < value.x && sX > value.x + value.w && sY < value.y && sY > value.y + value.h) {
                    // 鼠标在左上方向生成的矩形中
                    iem = index;
                    judgeDraw(cav, ctx, list, iem);
                }
                if (iem === undefined) {
                    // 鼠标不在矩形中
                    newDraw(cav, ctx, list);
                }
            })
        } else { // **** 已有选中矩形 ****
            // 判断鼠标位置
            for (let index = 0; index < list.length; index++) {
                let value = list[index];
                if (sX < value.x + 5 && sX > value.x - 5 && sY < value.y + 5 && sY > value.y - 5) {
                    // ***  鼠标在起点角  ***
                    if (index === i) {
                        changeDraw(cav, ctx, list, i, 1);
                        break;
                    }
                } else if (sX < value.x + value.w + 5 && sX > value.x + value.w - 5 && sY < value.y + 5 && sY > value.y - 5) {
                    // ***  鼠标在起点横向角  ***
                    if (index === i) {
                        changeDraw(cav, ctx, list, i, 2);
                        break;
                    }
 
                } else if (sX < value.x + 5 && sX > value.x - 5 && sY < value.y + value.h + 5 && sY > value.y + value.h - 5) {
                    // ***  鼠标在起点纵向角  ***
                    if (index === i) {
                        changeDraw(cav, ctx, list, i, 3);
                        break;
                    }
 
                } else if (sX < value.x + value.w + 5 && sX > value.x + value.w - 5 && sY < value.y + value.h + 5 && sY > value.y + value.h - 5) {
                    // ***  鼠标在终点角  ***
                    if (index === i) {
                        changeDraw(cav, ctx, list, i, 4);
                        break;
                    }
 
                } else if (value.w > 0 && value.h > 0 && sX > value.x && sX < value.x + value.w && sY > value.y && sY < value.y + value.h) {
                    // ***  鼠标在右下方向生成的矩形中  ***
                    iem = index
                    judgeDraw(cav, ctx, list, index);
                    break;
 
                } else if (value.w < 0 && value.h > 0 && sX < value.x && sX > value.x + value.w && sY > value.y && sY < value.y + value.h) {
                    // ***  鼠标在左下方向生成的矩形中  ***
                    iem = index
                    judgeDraw(cav, ctx, list, index);
                    break;
 
                } else if (value.w > 0 && value.h < 0 && sX > value.x && sX < value.x + value.w && sY < value.y && sY > value.y + value.h) {
                    // ***  鼠标在右上方向生成的矩形中  ***
                    iem = index
                    judgeDraw(cav, ctx, list, index);
                    break;
 
                } else if (value.w < 0 && value.h < 0 && sX < value.x && sX > value.x + value.w && sY < value.y && sY > value.y + value.h) {
                    // ***  鼠标在左上方向生成的矩形中  ***
                    iem = index
                    judgeDraw(cav, ctx, list, index);
                    break;
 
                } else {
                    if (iem === undefined) {
                        // *** 鼠标不在矩形中 ***
                        newDraw(cav, ctx, list);
                    }
                }
            }
        }
 
        /* 鼠标移出画布区域时保存选中矩形下标(如有) */
        cav.onmouseout = function (eo) {
            if (i !== undefined) {
                // 初始化
                draw(cav, list, i);
            }
        };
    }
};
 
/* 编辑矩形四个角 */
function changeDraw(cav, ctx, list, i, site) {
    cav.style.cursor = 'pointer'
 
    // site: 操作矩形角的位置, 1-起点 2-起点横向 3-起点纵向 4-终点
    let mark = list[i];
 
    /* 按下鼠标左键 */
    cav.onmousedown = function (ed) {
        // 保存鼠标落下位置的X, Y坐标, firefox中鼠标移动后ed.offsetX ed.offsetY会变成 0, 需要使用临时参数存储起来
        let sX = ed.offsetX; // 起点X坐标
        let sY = ed.offsetY; // 起点Y坐标
 
        /* 移动鼠标 */
        cav.onmousemove = function (em) {
            // 计算绘制数据
            let iframe = {}
            switch (site) {
                case 1:
                    iframe = {
                        x: em.offsetX,
                        y: em.offsetY,
                        w: mark.w - (em.offsetX - sX),
                        h: mark.h - (em.offsetY - sY)
                    }
                    break;
                case 2:
                    iframe = {
                        x: mark.x,
                        y: mark.y + (em.offsetY - sY),
                        w: mark.w + (em.offsetX - sX),
                        h: mark.h - (em.offsetY - sY)
                    }
                    break;
                case 3:
                    iframe = {
                        x: mark.x + (em.offsetX - sX),
                        y: mark.y,
                        w: mark.w - (em.offsetX - sX),
                        h: mark.h + (em.offsetY - sY)
                    }
                    break;
                case 4:
                    iframe = {
                        x: mark.x,
                        y: mark.y,
                        w: mark.w + (em.offsetX - sX),
                        h: mark.h + (em.offsetY - sY)
                    }
                    break;
            }
            list.splice(i, 1, iframe);
 
            // 重新绘制
            reDraw(cav, ctx, list, i);
        }
 
        /* 鼠标离开矩形区 */
        cav.onmouseout = function (eo) {
            // 重新绘制
            reDraw(cav, ctx, list);
            // 初始化
            draw(cav, list)
        };
 
        /* 监听键盘, 点击后可以控制删除, 由于移动矩形事件已经监听了onmousemove, 所以在移动矩形方法中仍有一次调用 */
        delDraw(cav, ctx, list, i);
    }
 
};
 
/* 绘制新矩形 */
function newDraw(cav, ctx, list) {
    cav.style.cursor = 'crosshair'
    // 初始化变量
    let start = false; // 画框状态, false时不执行画框操作
    let sX = 0; // 起点X坐标
    let sY = 0; // 起点Y坐标
 
    /* 按下鼠标左键 */
    cav.onmousedown = function (ed) {
        /* 使用变量 */
        start = true;
        sX = ed.offsetX;
        sY = ed.offsetY;
 
        /* 重置按键监听, 防止选中取消后仍可删除 */
        delDraw(cav, ctx, list, null)
 
        /* 鼠标移动 */
        cav.onmousemove = function (em) {
            if (start) {
                // 重新绘制
                reDraw(cav, ctx, list);
                // 设置边框为虚线
                ctx.beginPath();
                ctx.setLineDash([8, 4]);
                ctx.rect(sX, sY, em.offsetX - sX, em.offsetY - sY);
                ctx.stroke();
            }
        }
 
        /* 鼠标抬起 */
        cav.onmouseup = function (eu) {
            if (start && Math.abs(eu.offsetX - sX) > 10 && Math.abs(eu.offsetY - sY) > 10) {
                // 改变矩形数组
                let frame = {
                    x: sX, y: sY, w: eu.offsetX - sX, h: eu.offsetY - sY
                };
                list.push(frame);
                // 重新绘制
                reDraw(cav, ctx, list);
                // 改变画框状态
                start = false
                // 初始化
                draw(cav, list)
            } else {
                // 重新绘制
                reDraw(cav, ctx, list);
                // 改变画框状态
                start = false
                // 初始化
                draw(cav, list)
            }
        };
 
        /* 鼠标离开矩形区 */
        cav.onmouseout = function (eo) {
            if (start && Math.abs(eo.offsetX - sX) > 10 && Math.abs(eo.offsetY - sY) > 10) {
                // 改变矩形数组
                let frame = {
                    x: sX, y: sY, w: eo.offsetX - sX, h: eo.offsetY - sY
                };
                list.push(frame);
                // 重新绘制
                reDraw(cav, ctx, list);
                // 改变画框状态
                start = false;
                // 初始化
                draw(cav, list)
            } else {
                // 重新绘制
                reDraw(cav, ctx, list);
                // 改变画框状态
                start = false
                // 初始化
                draw(cav, list)
            }
        };
    }
};
 
/* 选中矩形, 重绘矩形, 并分发后续事件 */
function judgeDraw(cav, ctx, list, iem) {
    cav.style.cursor = 'default'
    // 初始化变量
    let sX = 0; // 起点X坐标
    let sY = 0; // 起点Y坐标
 
    /* 按下鼠标左键 */
    cav.onmousedown = function (ed) {
        sX = ed.offsetX;
        sY = ed.offsetY;
 
        // 更改选中状态, 重绘矩形
        reDraw(cav, ctx, list, iem);
 
        /* 当仅点击选中矩形便抬起鼠标后, 重新初始化画布 */
        cav.onmouseup = function () {
            // 重绘矩形
            reDraw(cav, ctx, list, iem);
 
            // 初始化
            draw(cav, list, iem);
        };
 
        /* 按住拖动鼠标, 移动选中矩形*/
        moveDraw(cav, ctx, list, iem, sX, sY);
 
        /* 监听键盘, 点击后可以控制删除, 由于移动矩形事件已经监听了onmousemove, 所以在移动矩形方法中仍有一次调用 */
        delDraw(cav, ctx, list, iem);
    }
};
 
/* 移动矩形 */
function moveDraw(cav, ctx, list, i, sX, sY) {
    let mark = list[i]
    cav.onmousemove = function (em) {
        let iframe = {
            x: mark.x + (em.offsetX - sX),
            y: mark.y + (em.offsetY - sY),
            w: mark.w,
            h: mark.h
        }
        list.splice(i, 1, iframe);
        /* 监听键盘, 使矩形在移动后仍可删除, 在点击未移动过的矩形时仍有一次监听 */
        delDraw(cav, ctx, list, i);
        // 重新绘制
        reDraw(cav, ctx, list, i);
    }
 
    cav.onmouseup = function () {
        // 重绘矩形
        reDraw(cav, ctx, list, i);
 
        // 初始化
        draw(cav, list, i);
    };
};
 
/* 删除矩形 */
function delDraw(cav, ctx, list, i) {
    /* 按键事件 */
    if (i === null) {
        // i为null时阻止按键监听事件冒泡
        cav.onkeydown = function (k) {
            return false;
        }
    } else {
        // 监听按键事件
        cav.onkeydown = function (k) {
            let key = k.keyCode || k.which;
            if (key == 8 && i !== null) {
                if (list.length >= 1) {
                    // 删除数组元素
                    list.splice(i, 1);
                    // 重绘矩形
                    reDraw(cav, ctx, list);
                } else {
                    /* 矩形数组长度为0, 已将矩形框全部删除 */
                    ctx.clearRect(0, 0, cav.width, cav.height);
                }
                // 重置监听状态, 防止删除完毕后, 按键监听不消失
                delDraw(cav, ctx, list, null)
                // 重绘矩形
                reDraw(cav, ctx, list);
                // 初始化
                draw(cav, list);
            }
        }
    }
};
 
/* 重绘所有矩形 */
function reDraw(cav, ctx, list, i) {
    ctx.setLineDash([8, 0]); // 设置边框为实线
    ctx.clearRect(0, 0, cav.width, cav.height);
    // 绘制未选中部分
    list.forEach(function (value, index, array) {
        if (i === undefined || index != i) {
            ctx.beginPath();
            ctx.strokeStyle = 'blue';
            ctx.rect(value.x, value.y, value.w, value.h);
            ctx.stroke();
        }
    });
    // 绘制已选中部分
    list.forEach(function (value, index, array) {
        if (index === i) {
            /* 绘制方框 */
            ctx.beginPath();
            ctx.strokeStyle = 'red';
            ctx.rect(value.x, value.y, value.w, value.h);
            ctx.fillStyle = 'RGBA(102,102,102,0.2)'
            ctx.fillRect(value.x, value.y, value.w, value.h);
            ctx.stroke();
            // 绘制四个角的圆圈
            ctx.beginPath();
            ctx.strokeStyle = 'red';
            ctx.arc(value.x, value.y, 4, 0, Math.PI * 2)
            ctx.fillStyle = "red";
            ctx.fill();// 画起点实心圆
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(value.x, value.y + value.h, 4, 0, Math.PI * 2);
            ctx.fillStyle = "red";
            ctx.fill();// 画起点纵向实心圆
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(value.x + value.w, value.y + value.h, 4, 0, Math.PI * 2);
            ctx.fillStyle = "red";
            ctx.fill();// 画起点横向实心圆
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(value.x + value.w, value.y, 4, 0, Math.PI * 2);
            ctx.fillStyle = "red";
            ctx.fill();// 画终点实心圆
            ctx.stroke();
        }
    })
};