const frmSearchFilter = document.forms.frmSearchFilter;
const frmSearchResult = document.forms.frmSearchResult;
const btnSearchNetflix = document.querySelector("#btnSearchNetflix");
const btnSaveVideos = document.querySelector("#btnSaveVideos");

// 검색 버튼 이벤트 리스너
btnSearchNetflix?.addEventListener("click", function (e) {
    e.preventDefault();
    frmSearchFilter.submit();
});

// 저장 버튼 이벤트 리스너
btnSaveVideos?.addEventListener("click", function (e) {
    e.preventDefault();
    const checkedVideos = document.querySelectorAll("input[name=ext_ids]:checked");
    if (checkedVideos.length === 0) {
        alert("선택된 데이터가 없습니다.");
        return;
    }
    frmSearchResult.submit();
});

// 체크박스 전체 선택/해제
const chkVideoAll = document.querySelector("#chkVideoAll");
chkVideoAll.addEventListener('click', () => {
    const checkAllValue = chkVideoAll.checked;
    const checkVideos = document.querySelectorAll("input[name=ext_ids]")
    checkVideos.forEach((checkVideo) => {
        checkVideo.checked = checkAllValue;
    })
});