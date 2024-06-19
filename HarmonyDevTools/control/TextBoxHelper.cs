using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace HarmonyDevTools.control;

public static class TextBoxHelper
{
    public static readonly DependencyProperty PlaceholderProperty =
        DependencyProperty.RegisterAttached("Placeholder", typeof(string), typeof(TextBoxHelper),
            new PropertyMetadata(default(string), OnPlaceholderChanged));

    public static void SetPlaceholder(UIElement element, string value)
    {
        element.SetValue(PlaceholderProperty, value);
    }

    public static string GetPlaceholder(UIElement element)
    {
        return (string)element.GetValue(PlaceholderProperty);
    }

    private static void OnPlaceholderChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is TextBox textBox)
        {
            textBox.GotFocus -= RemovePlaceholder;
            textBox.LostFocus -= ShowPlaceholder;

            if (!string.IsNullOrEmpty((string)e.NewValue))
            {
                textBox.GotFocus += RemovePlaceholder;
                textBox.LostFocus += ShowPlaceholder;

                ShowPlaceholder(textBox, null);
            }
        }
    }

    private static void RemovePlaceholder(object sender, RoutedEventArgs e)
    {
        if (sender is TextBox textBox && textBox.Text == GetPlaceholder(textBox))
        {
            textBox.Text = "";
            textBox.Foreground = Brushes.Black;
        }
    }

    private static void ShowPlaceholder(object sender, RoutedEventArgs e)
    {
        if (sender is TextBox textBox && string.IsNullOrEmpty(textBox.Text))
        {
            textBox.Text = GetPlaceholder(textBox);
            textBox.Foreground = Brushes.Gray;
        }
    }
}