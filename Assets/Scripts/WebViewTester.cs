using UnityEngine;
using UnityEngine.UI;

public class WebViewTester : MonoBehaviour
{
    // 웹뷰 매니저 참조
    public WebViewManager webViewManager;
    
    // 테스트용 UI 버튼들
    public Button openButton;
    public Button closeButton;
    
    void Start()
    {
        // WebViewManager가 설정되지 않았다면 자동으로 찾기
        if (webViewManager == null)
        {
            webViewManager = FindObjectOfType<WebViewManager>();
        }
        
        // 버튼에 이벤트 연결
        if (openButton != null)
        {
            openButton.onClick.AddListener(OpenWebView);
        }
        
        if (closeButton != null)
        {
            closeButton.onClick.AddListener(CloseWebView);
        }
    }
    
    // 웹뷰 열기
    public void OpenWebView()
    {
        if (webViewManager != null)
        {
            Debug.Log("WebViewTester: 웹뷰 열기 시도");
            StartCoroutine(webViewManager.LoadWebView());
        }
        else
        {
            Debug.LogError("WebViewTester: WebViewManager가 설정되지 않았습니다.");
        }
    }
    
    // 웹뷰 닫기
    public void CloseWebView()
    {
        if (webViewManager != null)
        {
            Debug.Log("WebViewTester: 웹뷰 닫기 시도");
            webViewManager.CloseWebView();
        }
    }
    
    // URL 직접 로드 (외부에서 호출 가능)
    public void LoadURL(string url)
    {
        if (webViewManager != null && !string.IsNullOrEmpty(url))
        {
            // 여기서는 기존 LoadWebView를 사용하지만,
            // 필요하다면 WebViewManager에 직접 URL을 전달하는 
            // 메소드를 추가할 수 있습니다.
            StartCoroutine(webViewManager.LoadWebView());
        }
    }
    
    void OnDestroy()
    {
        if (openButton != null)
        {
            openButton.onClick.RemoveListener(OpenWebView);
        }
        
        if (closeButton != null)
        {
            closeButton.onClick.RemoveListener(CloseWebView);
        }
    }
} 