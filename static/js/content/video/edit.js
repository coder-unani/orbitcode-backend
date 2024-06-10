// 사용 가능한 아이디 목록 (항목별 최대 10개)
const newIds = {
    "thumbnail": [
        {"id": "new1", "usage": false},
        {"id": "new2", "usage": false},
        {"id": "new3", "usage": false},
        {"id": "new4", "usage": false},
        {"id": "new5", "usage": false},
        {"id": "new6", "usage": false},
        {"id": "new7", "usage": false},
        {"id": "new8", "usage": false},
        {"id": "new9", "usage": false},
        {"id": "new10", "usage": false}
    ],
    "watch": [
        {"id": "new1", "usage": false},
        {"id": "new2", "usage": false},
        {"id": "new3", "usage": false},
        {"id": "new4", "usage": false},
        {"id": "new5", "usage": false},
        {"id": "new6", "usage": false},
        {"id": "new7", "usage": false},
        {"id": "new8", "usage": false},
        {"id": "new9", "usage": false},
        {"id": "new10", "usage": false}
    ],
    "genre": [
        {"id": "new1", "usage": false},
        {"id": "new2", "usage": false},
        {"id": "new3", "usage": false},
        {"id": "new4", "usage": false},
        {"id": "new5", "usage": false},
        {"id": "new6", "usage": false},
        {"id": "new7", "usage": false},
        {"id": "new8", "usage": false},
        {"id": "new9", "usage": false},
        {"id": "new10", "usage": false}
    ],
    "actor": [
        {"id": "new1", "usage": false},
        {"id": "new2", "usage": false},
        {"id": "new3", "usage": false},
        {"id": "new4", "usage": false},
        {"id": "new5", "usage": false},
        {"id": "new6", "usage": false},
        {"id": "new7", "usage": false},
        {"id": "new8", "usage": false},
        {"id": "new9", "usage": false},
        {"id": "new10", "usage": false}
    ],
    "staff": [
        {"id": "new1", "usage": false},
        {"id": "new2", "usage": false},
        {"id": "new3", "usage": false},
        {"id": "new4", "usage": false},
        {"id": "new5", "usage": false},
        {"id": "new6", "usage": false},
        {"id": "new7", "usage": false},
        {"id": "new8", "usage": false},
        {"id": "new9", "usage": false},
        {"id": "new10", "usage": false}
    ],
};

// 썸네일 타입 정의
const THUMBNAIL_TYPE = [
    {"value": "10", "text": "세로"},
    {"value": "11", "text": "가로"}
];

// 시청정보 타입 정의
const WATCH_TYPE = [
    {"value": "10", "text": "Netflix"},
    {"value": "11", "text": "Disney+"},
    {"value": "12", "text": "Tving"},
    {"value": "13", "text": "Wavve"},
];

// 배우 타입 정의
const ACTOR_TYPE = [
    {"value": "10", "text": "주연"},
    {"value": "11", "text": "조연"},
    {"value": "12", "text": "단역"},
];

// 스태프 타입 정의
const STAFF_TYPE = [
    {"value": "10", "text": "감독"},
    {"value": "11", "text": "작가"},
    {"value": "12", "text": "제작"},
];

// 아이디 발행
const publishId = (prefix) => {
    let id = "";
    for (const item of newIds[prefix]) {
        if (!item.usage) {
            id = item.id;
            item.usage = true;
            break;
        }
    }
    if (id) {
        const createIds = document.querySelector(`input[name=${prefix}_create]`);
        let createIdsArray = [];
        if (createIds.value.length > 0) {
            createIdsArray = createIds.value.split(',');
        }
        createIdsArray.push(id);
        createIds.value = createIdsArray.join(',');
    }

    return id;
}

// 아이디 사용 중지
const unpublishId = (prefix, id) => {
    for (const item of newIds[prefix]) {
        if (item.id === id) {
            item.usage = false;
        }
    }
    const createIds = document.querySelector(`input[name=${prefix}_create]`);
    let createIdsArray = [];
    if (createIds.value.length > 0) {
        createIdsArray = createIds.value.split(',');
    }
    const index = createIdsArray.indexOf(id);
    if (index > -1) {
        createIdsArray.splice(index, 1);
    }
    createIds.value = createIdsArray.join(',');
    return true;
}

// 엘리멘트 추가
const addElement = (prefix, options = []) => {
    const container = document.querySelector(`#${prefix}_container`);
    const newDiv = document.createElement('div');

    const id = publishId(prefix);
    if (id === "") {
        alert(`${prefix}는 최대 ${newIds[prefix].length}개까지 등록 가능합니다.`);
        return;
    }

    newDiv.id = `${prefix}_wrap_${id}`;
    newDiv.classList.add('flex', 'gap-2.5', 'w-full');

    if (options.length > 0) {
        const select = document.createElement('select');
        select.name = `${prefix}_type_${id}`;
        select.classList.add('form-select', 'w-[100px]');
        options.map((option) => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.textContent = option.text;
            select.appendChild(opt);
        });
        newDiv.appendChild(select);
    }

    const newInput = document.createElement('input');
    newInput.type = "text";
    newInput.name = `${prefix}_${id}`;
    newInput.classList.add('form-input', 'rounded-lg');
    newDiv.appendChild(newInput);

    const newButton = document.createElement('button');
    newButton.type = "button";
    newButton.classList.add(
        'bg-danger', 'text-white', 'rounded-[10px]', 'h-12', 'w-12', 'flex', 'justify-center', 'items-center'
    );
    newButton.textContent = "-";
    newButton.dataset.id = id;
    newButton.addEventListener('click', () => {
        removeElement(prefix, id);
    });
    newDiv.appendChild(newButton);

    container.appendChild(newDiv);
}

// 엘리멘트 삭제
const removeElement = (prefix, id) => {
    const container = document.querySelector(`#${prefix}_wrap_${id}`);
    const origin = container.querySelector(`input[name=${prefix}_origin_${id}]`)
    unpublishId(prefix, id);
    if (origin !== null && origin !== undefined) {
        const originId = id;
        const deleteIds = document.querySelector(`input[name=${prefix}_delete]`);
        let deleteIdsArray = [];
        if (deleteIds.value.length > 0) {
            deleteIdsArray = deleteIds.value.split(',');
        }
        deleteIdsArray.push(originId);
        deleteIds.value = deleteIdsArray.join(',');
    }
    container.remove();
}