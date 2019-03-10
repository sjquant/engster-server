import {
  search
} from "~/api";

export default {
  FETCH_LINE_ENGLISH({
    commit
  }, keyword) {
    return search.fetchEnglish(keyword).then(data => {
      console.log(data)
    })
  },
  FETCH_LINE_KOREAN({
    commit
  }, keyword) {
    return search.fetchKorean(keyword).then(data => {
      console.log(data)
    })
  }
};
