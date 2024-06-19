const frmSearchFilter = document.forms.frmSearchFilter;
const frmSearchResult = document.forms.frmSearchResult;
const iptFilterIn = document.querySelector("#iptFilterIn");
const iptSearchFilters = document.querySelector("#iptSearchFilters");
const divSearchFilter = document.querySelector("#divFilter");
const btnAddFilter = document.querySelector("#btnAddFilter");
const btnSearchFilter = document.querySelector("#btnSearchFilter");
const btnSaveVideos = document.querySelector("#btnSaveVideos");
const iptSaveVideoIds = document.querySelector("#iptSaveVideoIds");

// 입력 필터(ID)값 가져오기
const getFilterIn = () => {
    return iptFilterIn.value.split(",");
}

// 필터 입력창 초기화
const resetFilterIn = () => {
    iptFilterIn.value = "";
}

// 셋팅된 검색필터 가져오기
const getSearchFilter = () => {
    return iptSearchFilters.value.split(",");
}

// 검색필터 셋팅하기
const setSearchFilter = (arrFilter) => {
    iptSearchFilters.value = arrFilter.join(",");
}

// 검색필터 화면 출력
const dispSearchFilter = (arrFilter) => {
    // 검색필터 화면출력
    arrFilter.map((id) => {
        if (id.length > 0) {
            let dispFilter = document.createElement("button");
            dispFilter.setAttribute("type", "button")
            dispFilter.setAttribute("class", "flex items-center px-2 bg-primary border border-primary rounded-md text-white transition-all duration-300 hover:bg-primary");
            dispFilter.innerHTML = `
                <span class="pl-1.5">${id}</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle opacity="0.5" cx="12" cy="12" r="10" stroke="none" stroke-width="1.5"/>
                    <path d="M14.5 9.50002L9.5 14.5M9.49998 9.5L14.5 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>`;
            dispFilter.addEventListener('click', () => removeSearchFilter(id));
            divSearchFilter.appendChild(dispFilter);
        }
    });
}

// 검색필터 추가하기
const addSearchFilter = () => {
    // 검색필터 화면출력 초기화
    divSearchFilter.innerHTML = "";
    // 검색필터 배열로 가져오기
    const arrFilter = getFilterIn();
    const arrSearchFilter = getSearchFilter();
    // 검색필터에 입력된 검색필터 추가
    arrFilter.map((id) => {
        arrSearchFilter.push(id)
    });
    // 중복 제거 및 가비지 항목 제거
    let arrNewSearchFilter = Array();
    arrSearchFilter.map((id) => {
       if (arrNewSearchFilter.indexOf(id) < 0 && id.trim().length > 0) {
           arrNewSearchFilter.push(id);
       }
    });
    // 검색필터 등록
    setSearchFilter(arrNewSearchFilter);
    // 검색필터 화면출력
    dispSearchFilter(arrNewSearchFilter);
    // 필터입력 초기화
    resetFilterIn();
}

// 검색필터 삭제하기
const removeSearchFilter = (filter) => {
    // 검색필터 화면출력 초기화
    divSearchFilter.innerHTML = "";
    // 검색필터 배열로 가져오기
    const arrSearchFilter = getSearchFilter();
    // 검색필터 삭제
    arrSearchFilter.map((value, index) => {
        if (value === filter) {
            arrSearchFilter.splice(index, 1);
        }
    });
    // 검색필터 등록
    setSearchFilter(arrSearchFilter);
    // 검색필터 화면출력
    dispSearchFilter(arrSearchFilter);
}

// 검색 필터 추가 이벤트리스너
btnAddFilter?.addEventListener("click", function (e) {
    e.preventDefault();
    addSearchFilter();
});

// 필터 입력창 키보드 이벤트리스너
iptFilterIn?.addEventListener("keyup", function (e) {
    if (e.keyCode === 13) {
        addSearchFilter();
    }
});

// 검색 버튼 이벤트 리스너
btnSearchFilter?.addEventListener("click", function (e) {
    e.preventDefault();
    frmSearchFilter.submit();
});

// 저장 버튼 이벤트 리스너
btnSaveVideos?.addEventListener("click", function (e) {
    e.preventDefault();
    const checkVideos = document.querySelectorAll("input[name=platform_ids]")
    let isCheckedVideo = false;
    checkVideos.forEach((checkVideo) => {
        if (checkVideo.checked) {
            isCheckedVideo = true;
        }
    });
    if (!isCheckedVideo) {
        alert("선택된 데이터가 없습니다.");
        return;
    }
    frmSearchResult.submit();
});

// 체크박스 전체 선택/해제
const chkVideoAll = document.querySelector("#chkVideoAll");
chkVideoAll?.addEventListener('click', () => {
    const checkAllValue = chkVideoAll.checked;
    const checkVideos = document.querySelectorAll("input[name=platform_ids]")
    checkVideos.forEach((checkVideo) => {
        checkVideo.checked = checkAllValue;
    })
});