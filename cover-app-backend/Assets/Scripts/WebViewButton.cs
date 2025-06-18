using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class WebViewButton : MonoBehaviour
{
    private Button button;
    private WebViewManager webViewManager;
    
    // 버튼 클릭 시 웹뷰 표시 여부
    public bool showWebViewOnClick = true;

    void Start()
    {
        button = GetComponent<Button>();
        webViewManager = FindObjectOfType<WebViewManager>();
        
        if (button != null && webViewManager != null)
        {
            button.onClick.AddListener(OnButtonClick);
        }
        else
        {
            Debug.LogError("WebViewButton: Button 또는 WebViewManager를 찾을 수 없습니다.");
        }
    }

    void OnButtonClick()
    {
        if (webViewManager != null)
        {
            if (showWebViewOnClick)
            {
                StartCoroutine(webViewManager.LoadWebView());
                webViewManager.ShowWebView(true);
            }
            else
            {
                webViewManager.CloseWebView();
            }
        }
    }

    void OnDestroy()
    {
        if (button != null)
        {
            button.onClick.RemoveListener(OnButtonClick);
        }
    }
} 