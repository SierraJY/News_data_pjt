/**
 * 백엔드에서 반환되는 키워드 문자열을 배열로 변환하는 유틸리티 함수
 * 
 * @param {any} keywords - 키워드 데이터 (문자열, 배열 등)
 * @returns {Array} - 처리된 키워드 배열
 */
export function parseKeywords(keywords) {
  if (!keywords) return [];
  
  // 이미 배열인 경우 그대로 반환
  if (Array.isArray(keywords)) return keywords;
  
  // 문자열인 경우 처리
  if (typeof keywords === 'string') {
    // 문자열이 '[', ']'로 둘러싸인 경우 제거
    let processedKeywords = keywords.trim();
    if (processedKeywords.startsWith('[') && processedKeywords.endsWith(']')) {
      processedKeywords = processedKeywords.substring(1, processedKeywords.length - 1);
    }
    
    try {
      // JSON 형식의 문자열인지 먼저 시도
      return JSON.parse(`[${processedKeywords}]`);
    } catch (e) {
      // JSON 파싱에 실패하면 일반 쉼표로 구분된 문자열로 처리
      return processedKeywords.split(',').map(k => k.trim());
    }
  }
  
  // 다른 형식의 경우 빈 배열 반환
  return [];
}