// src/utils/TemplateDownloadHelper.js
import Swal from 'sweetalert2';

export class TemplateDownloadHelper {
  static async downloadFromResponse(response, defaultFileName = 'template.xlsx') {
    try {
      if (response.data instanceof Blob) {
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        
        const contentDisposition = response.headers['content-disposition'];
        let fileName = defaultFileName;
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
            if (fileNameMatch && fileNameMatch.length === 2)
                fileName = fileNameMatch[1];
        }
        
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
        return true;
      }
      else if (response.data && response.data.downloadUrl) {
        const link = document.createElement('a');
        link.href = response.data.downloadUrl;
        link.download = response.data.fileName || defaultFileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return true;
      } else {
        this.generateFallbackTemplate(defaultFileName);
        return false;
      }
    } catch (error) {
      console.error('Download template error:', error);
      Swal.fire("Error!", "Failed to download template.", "error");
      return false;
    }
  }

  static generateFallbackTemplate(fileName) {
    const templateType = this.getTemplateType(fileName);
    const data = this.getFallbackTemplateData(templateType);
    
    this.downloadCSV(data, fileName.replace('.xlsx', '.csv'));
    
    Swal.fire({
      title: "📄 Template Generated",
      html: `
        <div style="text-align: left;">
          <p>A sample template has been generated for you.</p>
          <div style="background: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 10px; margin: 10px 0;">
            <strong style="color: #2e7d32;">✅ What to do next:</strong>
            <ol style="margin: 5px 0; padding-left: 20px; color: #2e7d32;">
              <li>Open the downloaded CSV file</li>
              <li>Follow the sample data format</li>
              <li>Replace sample data with your actual data</li>
              <li>Save and import the file</li>
            </ol>
          </div>
          <p style="color: #666; font-size: 14px;">
            <strong>Note:</strong> For the official template with complete validation, please contact your administrator.
          </p>
        </div>
      `,
      icon: "success",
      confirmButtonText: "Understand",
      confirmButtonColor: '#4caf50'
    });
  }

  static getTemplateType(fileName) {
    if (fileName.includes('phoneme_material') || fileName.includes('word')) {
      return 'phoneme_words';
    } else if (fileName.includes('exercise_phoneme') || fileName.includes('sentence')) {
      return 'exercise_sentences';
    } else if (fileName.includes('exam_phoneme') || fileName.includes('exam')) {
      return 'exam_sentences';
    } else if (fileName.includes('talent')) {
      return 'talent';
    }
    return 'general';
  }

  static getFallbackTemplateData(templateType) {
    switch (templateType) {
      case 'talent':
        return [
          ['nama', 'email', 'role', 'password'],
          ['Brahmantya', 'brahmantyaganteng@gmail.com', 'Mobile Developer', 'Brahmantya987'],
          ['Hafidzon', 'hafidzonganteng@gmail.com', 'Backend Developer', 'Hafidzon987'],
          ['Vico', 'vicoganteng@gmail.com', 'Full Stack Developer', 'Vico987']
        ];
      case 'phoneme_words':
        return [
          ['kategori', 'kata', 'fonem', 'arti', 'definisi'],
          ['i', 'believe', 'bɪliv', 'percaya', 'Menerima sesuatu sebagai kebenaran.'],
          ['ɪ', 'with', 'wɪð', 'dengan', 'Ditemani oleh; bersama.'],
          ['p', 'push', 'pʊʃ', 'mendorong', 'Memberi tekanan agar bergerak maju.']
        ];
      case 'exercise_sentences':
        return [
          ['kategori', 'kalimat', 'fonem'],
          ['i-ɪ', 'He did see if this big team is really in it.', 'hi dɪd si ɪf ðɪs bɪg tim ɪz rɪəli ɪn ɪt'],
          ['p-b', 'The big problem is people buy poor quality baby products.', 'ðə bɪg prɔbləm ɪz pipəl baɪ pʊər kwɔləti beɪbi prɔdʌkts']
        ];
      default:
        return [
          ['Column1', 'Column2', 'Column3'],
          ['Sample Data 1', 'Sample Data 2', 'Sample Data 3'],
          ['Example 1', 'Example 2', 'Example 3']
        ];
    }
  }

  static downloadCSV(data, fileName) {
    const csvContent = data.map(row => 
      row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', fileName);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  static getImportInstructions(materialType) {
    switch (materialType.toLowerCase()) {
      case 'phoneme material':
        return `
          <div style="text-align: left; max-height: 70vh; overflow-y: auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
              <h3 style="margin: 0; color: white;">📝 Phoneme Material Import</h3>
              <p style="margin: 5px 0 0 0; opacity: 0.9;">Import individual words with phoneme categories and transcriptions</p>
            </div>
            <div style="background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin-bottom: 15px;">
              <h4 style="color: #2e7d32; margin-top: 0;">✅ Import Rules</h4>
              <ul style="margin: 0; padding-left: 20px; color: #2e7d32;">
                <li>Use single phoneme categories (e.g., <code>i</code>, <code>ɪ</code>, <code>p</code>, <code>b</code>)</li>
                <li>Phoneme transcription must contain the category phoneme</li>
                <li>All columns are required: kategori, kata, arti, definisi, fonem</li>
              </ul>
            </div>
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px;">
              <h4 style="color: #1976d2; margin-top: 0;">📋 File Requirements</h4>
              <ul style="margin: 0; padding-left: 20px; color: #1976d2;">
                <li>Format: .xlsx or .csv</li>
                <li>Maximum size: 10MB</li>
              </ul>
            </div>
          </div>
        `;
      
      case 'exercise phoneme':
        return `
          <div style="text-align: left; max-height: 70vh; overflow-y: auto;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
              <h3 style="margin: 0; color: white;">🎯 Exercise Phoneme Import</h3>
              <p style="margin: 5px 0 0 0; opacity: 0.9;">Import practice sentences for similar phonemes training</p>
            </div>
            <div style="background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin-bottom: 15px;">
              <h4 style="color: #2e7d32; margin-top: 0;">✅ Import Rules</h4>
              <ul style="margin: 0; padding-left: 20px; color: #2e7d32;">
                <li>Use similar phoneme categories (e.g., <code>i-ɪ</code>, <code>p-b</code>)</li>
                <li>Sentences must contain at least 10 words</li>
                <li>Phoneme transcription must contain ALL category phonemes</li>
              </ul>
            </div>
          </div>
        `;
      
      case 'exam phoneme':
        return `
          <div style="text-align: left; max-height: 70vh; overflow-y: auto;">
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
              <h3 style="margin: 0; color: white;">🎓 Exam Phoneme Import</h3>
            </div>
            <div style="background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin-bottom: 15px;">
              <h4 style="color: #2e7d32; margin-top: 0;">✅ Import Rules</h4>
              <ul style="margin: 0; padding-left: 20px; color: #2e7d32;">
                <li>Use similar phoneme categories (e.g., <code>i-ɪ</code>, <code>p-b</code>)</li>
                <li>Each exam must have exactly 10 sentences</li>
                <li>Each sentence must contain at least 10 words</li>
              </ul>
            </div>
          </div>
        `;
      
      
      case 'talent':
        return `
          <div style="text-align: left; max-height: 70vh; overflow-y: auto;">
            <div style="background: linear-gradient(135deg, #2196f3 0%, #0d47a1 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
              <h3 style="margin: 0; color: white;">👥 Talent Import</h3>
              <p style="margin: 5px 0 0 0; opacity: 0.9;">Import multiple new talent accounts at once</p>
            </div>
            <div style="background: #e8f5e8; border-left: 4px solid #4caf50; padding: 15px; margin-bottom: 15px;">
              <h4 style="color: #2e7d32; margin-top: 0;">✅ Import Rules</h4>
              <ul style="margin: 0; padding-left: 20px; color: #2e7d32;">
                <li>All columns are required: <strong>nama, email, role, password</strong></li>
                <li>Email must be unique and not already registered</li>
                <li>Password must be at least 6 characters long</li>
                <li>Email format must be valid (contain @ and .)</li>
              </ul>
            </div>
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px;">
              <h4 style="color: #1976d2; margin-top: 0;">📋 File Requirements</h4>
              <ul style="margin: 0; padding-left: 20px; color: #1976d2;">
                <li>Format: .xlsx or .csv</li>
                <li>Maximum size: 10MB</li>
                <li>Use UTF-8 encoding for CSV files</li>
              </ul>
            </div>
          </div>
        `;

      default:
        return `
          <div style="text-align: left;">
            <h4>General Import Instructions:</h4>
            <ul>
              <li>Follow the template format exactly</li>
              <li>All required fields must be filled</li>
            </ul>
          </div>
        `;
    }
  }
}

export default TemplateDownloadHelper;